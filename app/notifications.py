import json
import logging
import os
import re
import sys
import threading
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from winotify import Notification, Registry, audio

from .api_client import APIRequestError, api_request

logger = logging.getLogger(__name__)
APP_ID = "Medic Program"
APP_PROTOCOL = APP_ID.replace(" ", "-")
ACTION_NAME = re.compile(r"^(taken|not_taken)_([0-9a-f]{32})$")

PERIOD_TIMES = {
    1: (8, "08:00"),
    2: (12, "12:00"),
    3: (16, "16:00"),
    4: (20, "20:00"),
}


def _actions_directory():
    local_app_data = os.environ.get("LOCALAPPDATA")
    base = Path(local_app_data) if local_app_data else Path.home() / "AppData" / "Local"
    return base / "MedicProgram" / "notification_actions"


def _reminder_actions(user_id, medicines, period_id, scheduled_at):
    token = uuid.uuid4().hex
    actions_directory = _actions_directory()
    actions_directory.mkdir(parents=True, exist_ok=True)
    (actions_directory / f"{token}.json").write_text(
        json.dumps(
            {
                "userId": user_id,
                "medIds": [medicine["medId"] for medicine in medicines],
                "periodId": period_id,
                "date": scheduled_at.date().isoformat(),
            }
        ),
        encoding="utf-8",
    )
    action_prefix = f"{APP_PROTOCOL}:"
    return (
        ("กินแล้ว", f"{action_prefix}taken_{token}"),
        ("ไม่กิน", f"{action_prefix}not_taken_{token}"),
    )


def _process_notification_action(token, status):
    action_file = _actions_directory() / f"{token}.json"
    processing_file = _actions_directory() / f"{token}.processing"
    try:
        os.replace(action_file, processing_file)
    except FileNotFoundError:
        logger.info("Medication reminder action was already handled or has expired.")
        return

    try:
        with processing_file.open(encoding="utf-8") as action_data:
            context = json.load(action_data)
        api_request(
            "/user/med/log",
            {
                "userId": context["userId"],
                "medIds": context["medIds"],
                "periodId": context["periodId"],
                "date": context["date"],
                "status": status,
            },
        )
    except (OSError, ValueError, KeyError) as error:
        logger.exception("Could not read the medication reminder action context.")
        os.replace(processing_file, action_file)
        show_notification("บันทึกผลไม่สำเร็จ", str(error))
        return
    except APIRequestError as error:
        logger.error("Could not record medication reminder action: %s", error)
        os.replace(processing_file, action_file)
        show_notification("บันทึกผลไม่สำเร็จ", str(error))
        return

    try:
        processing_file.unlink()
    except OSError:
        logger.exception("Could not clean up the completed medication reminder action.")
    result = "กินยาแล้ว" if status == "taken" else "เลือกไม่กินยา"
    try:
        show_notification("บันทึกผลแล้ว", result)
    except OSError:
        logger.exception("Could not display the medication action confirmation.")


def start_notification_actions():
    action_argument = next(
        (
            argument
            for argument in sys.argv[1:]
            if is_notification_action_argument(argument)
        ),
        None,
    )
    if action_argument is not None:
        process_notification_action_argument(action_argument)
        return True

    if getattr(sys, "frozen", False):
        executable = f'"{sys.executable}"'
        script_path = ""
    else:
        executable_path = Path(sys.executable)
        if os.name == "nt":
            windowless_python = executable_path.with_name("pythonw.exe")
            if windowless_python.is_file():
                executable_path = windowless_python
        executable = f'"{executable_path}"'
        script_path = f'"{Path(__file__).with_name("notification_action.py").resolve()}"'

    registry = Registry(
        APP_ID,
        executable=executable,
        script_path=script_path,
        force_override=True,
    )
    return False


def is_notification_action_argument(argument):
    return isinstance(argument, str) and argument.casefold().startswith(
        f"{APP_PROTOCOL}:".casefold()
    )


def process_notification_action_argument(argument):
    if not is_notification_action_argument(argument):
        return False
    action_name = argument.partition(":")[2]
    match = ACTION_NAME.fullmatch(action_name)
    if match is None:
        logger.error("Ignored an invalid medication reminder action.")
        return False
    _process_notification_action(match.group(2), match.group(1))
    return True


def show_notification(title, message, actions=()):
    toast = Notification(
        app_id=APP_ID,
        title=title,
        msg=message,
        duration="long",
    )
    toast.set_audio(audio.Default, loop=False)
    for label, callback in actions:
        toast.add_actions(label, callback)
    toast.show()


def next_scheduled_time(period_ids, now=None):
    now = now or datetime.now()
    candidates = []
    for period_id in period_ids:
        period = PERIOD_TIMES.get(period_id)
        if period is None:
            continue
        hour, _ = period
        scheduled = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        if scheduled <= now:
            scheduled += timedelta(days=1)
        candidates.append(scheduled)
    return min(candidates) if candidates else None


def current_period_id(now=None):
    now = now or datetime.now()
    if now.hour < 8 or now.hour >= 20:
        return 4
    if now.hour < 12:
        return 1
    if now.hour < 16:
        return 2
    return 3


class MedicineReminder:
    def __init__(self):
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._schedule = {}
        self._user_id = None
        self._last_notified = None
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def update(self, user_id, user_medicines, catalog_medicines):
        medicine_by_id = {
            medicine.get("medId"): medicine
            for medicine in catalog_medicines
            if isinstance(medicine.get("medId"), str)
        }
        schedule = {}
        for user_medicine in user_medicines:
            medicine = medicine_by_id.get(user_medicine.get("medId"))
            if medicine is None:
                continue
            for period_id in user_medicine.get("timesPerDay", []):
                med_id = user_medicine.get("medId")
                if period_id not in PERIOD_TIMES or not isinstance(med_id, str):
                    continue
                schedule.setdefault(period_id, []).append(
                    {
                        "medId": med_id,
                        "description": self._medicine_description(
                            user_medicine, medicine
                        ),
                    }
                )
        with self._lock:
            self._schedule = schedule
            self._user_id = user_id

    @staticmethod
    def _medicine_description(user_medicine, medicine):
        name = medicine.get("medName", "ยา")
        value = user_medicine.get("value")
        unit = medicine.get("unitName", "")
        dose = f"{value:g} {unit}".strip() if isinstance(value, (int, float)) else ""
        food = {"before": "ก่อนอาหาร", "after": "หลังอาหาร"}.get(
            user_medicine.get("foodRequire")
        )
        details = [detail for detail in (dose, food) if detail]
        return f"{name} ({', '.join(details)})" if details else name

    def test_notification(self):
        with self._lock:
            schedule = {
                period_id: list(medicines)
                for period_id, medicines in self._schedule.items()
            }
            user_id = self._user_id
        period_ids = sorted(schedule)
        if not period_ids:
            raise ValueError("ยังไม่มีช่วงเวลาที่ตั้งแจ้งเตือน")
        if not isinstance(user_id, str):
            raise ValueError("ไม่พบผู้ใช้สำหรับบันทึกผลการแจ้งเตือน")

        now = datetime.now()
        period_id = current_period_id(now)
        medicines = schedule.get(period_id, [])
        if not medicines:
            raise ValueError(
                f"ไม่มีรายการยาในรอบปัจจุบัน "
                f"({PERIOD_TIMES[period_id][1]})"
            )

        times = ", ".join(PERIOD_TIMES[period_id][1] for period_id in period_ids)
        actions = _reminder_actions(user_id, medicines, period_id, now)
        medicine_list = "\n".join(
            medicine["description"] for medicine in medicines
        )
        message = (
            f"เวลาที่ตั้งไว้: {times}\n"
            f"รอบปัจจุบัน: {PERIOD_TIMES[period_id][1]}\n"
            f"ผลจะบันทึกสำหรับยา:\n{medicine_list}"
        )
        show_notification("ทดสอบการแจ้งเตือนยา", message, actions)

    def stop(self):
        self._stop_event.set()

    def _run(self):
        while not self._stop_event.wait(10):
            now = datetime.now()
            if now.minute != 0 or now.hour not in (8, 12, 16, 20):
                continue
            period_id = {8: 1, 12: 2, 16: 3, 20: 4}[now.hour]
            notification_key = (now.date(), period_id)
            with self._lock:
                medicines = list(self._schedule.get(period_id, []))
                user_id = self._user_id
                if (
                    not medicines
                    or not isinstance(user_id, str)
                    or notification_key == self._last_notified
                ):
                    continue
                self._last_notified = notification_key

            try:
                actions = _reminder_actions(
                    user_id, medicines, period_id, now
                )
            except OSError:
                logger.exception(
                    "Could not prepare actions for the medicine reminder toast."
                )
                actions = ()

            message = "\n".join(medicine["description"] for medicine in medicines)
            try:
                show_notification(
                    f"ถึงเวลากินยา ({PERIOD_TIMES[period_id][1]})",
                    message,
                    actions,
                )
            except OSError:
                logger.exception("Could not display the medicine reminder toast.")
