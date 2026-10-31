import logging
import threading
from datetime import datetime, timedelta

from winotify import Notification, audio

logger = logging.getLogger(__name__)

PERIOD_TIMES = {
    1: (8, "08:00"),
    2: (12, "12:00"),
    3: (16, "16:00"),
    4: (20, "20:00"),
}


def show_notification(title, message):
    toast = Notification(
        app_id="Medic Program",
        title=title,
        msg=message,
        duration="long",
    )
    toast.set_audio(audio.Default, loop=False)
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


class MedicineReminder:
    def __init__(self):
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._schedule = {}
        self._last_notified = None
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def update(self, user_medicines, catalog_medicines):
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
                if period_id not in PERIOD_TIMES:
                    continue
                schedule.setdefault(period_id, []).append(
                    self._medicine_description(user_medicine, medicine)
                )
        with self._lock:
            self._schedule = schedule

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
        period_ids = sorted(schedule)
        if not period_ids:
            raise ValueError("ยังไม่มีช่วงเวลาที่ตั้งแจ้งเตือน")

        times = ", ".join(PERIOD_TIMES[period_id][1] for period_id in period_ids)
        upcoming = next_scheduled_time(period_ids)
        message = f"เวลาที่ตั้งไว้: {times}\nรอบถัดไป: {upcoming:%H:%M}"
        show_notification("ทดสอบการแจ้งเตือนยา", message)

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
                if (
                    not medicines
                    or notification_key == self._last_notified
                ):
                    continue
                self._last_notified = notification_key

            try:
                message = "\n".join(medicines)
                show_notification(
                    f"ถึงเวลากินยา ({PERIOD_TIMES[period_id][1]})",
                    message,
                )
            except OSError:
                logger.exception("Could not display the medicine reminder toast.")
