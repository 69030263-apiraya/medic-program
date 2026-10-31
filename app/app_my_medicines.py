import math
import threading
from tkinter import messagebox
from urllib.parse import urlencode

import customtkinter as ctk

from .api_client import APIRequestError

TIME_PERIODS = {
    1: "เช้า",
    2: "กลางวัน",
    3: "เย็น",
    4: "ก่อนนอน",
}

FOOD_OPTIONS = {
    "ไม่ระบุ": None,
    "ก่อนอาหาร": "before",
    "หลังอาหาร": "after",
}


class MyMedicinesView(ctk.CTkFrame):
    def __init__(self, master, user, api_request, on_logout):
        super().__init__(master, fg_color="#F1F5F9")
        self.user = user
        self.api_request = api_request
        self.on_logout = on_logout
        self.medicine_types = []
        self.catalog_medicines = []
        self.user_medicines = []
        self.medicines_by_label = {}
        self.type_ids_by_name = {}
        self.busy_buttons = []
        self.is_busy = False
        self.error_after_id = None

        header = ctk.CTkFrame(self, fg_color="#0F766E", corner_radius=0, height=72)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(
            header,
            text="ข้อมูลยาของฉัน",
            font=("Helvetica", 20, "bold"),
            text_color="#FFFFFF",
        ).pack(side="left", padx=24)
        ctk.CTkLabel(
            header,
            text=f"ผู้ใช้: {user.get('userName', '-')}",
            font=("Helvetica", 12),
            text_color="#CCFBF1",
        ).pack(side="left", padx=12)
        self.logout_button = ctk.CTkButton(
            header,
            text="ออกจากระบบ",
            width=120,
            fg_color="#DC2626",
            hover_color="#B91C1C",
            command=self.logout,
        )
        self.logout_button.pack(side="right", padx=20)
        self.busy_buttons.append(self.logout_button)

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=14)

        self.status_label = ctk.CTkLabel(
            content, text="", anchor="w", wraplength=800, text_color="#475569"
        )
        self.status_label.pack(fill="x", pady=(0, 4))
        self.loading_bar = ctk.CTkProgressBar(content, mode="indeterminate", height=4)

        self.add_frame = ctk.CTkFrame(content, fg_color="#FFFFFF", corner_radius=12)
        self.add_frame.pack(side="bottom", fill="x", pady=(12, 0))
        ctk.CTkLabel(
            self.add_frame,
            text="เพิ่มยาของฉัน",
            font=("Helvetica", 15, "bold"),
            text_color="#0F172A",
        ).pack(anchor="w", padx=14, pady=(10, 4))

        selectors = ctk.CTkFrame(self.add_frame, fg_color="transparent")
        selectors.pack(fill="x", padx=14, pady=(0, 8))

        type_column = ctk.CTkFrame(selectors, fg_color="transparent")
        type_column.pack(side="left", expand=True, fill="x", padx=(0, 8))
        ctk.CTkLabel(type_column, text="ประเภทยา").pack(anchor="w", pady=(0, 4))
        self.type_option = ctk.CTkOptionMenu(
            type_column,
            values=["กำลังโหลด..."],
            height=36,
            command=self._on_type_selected,
        )
        self.type_option.pack(fill="x")

        medicine_column = ctk.CTkFrame(selectors, fg_color="transparent")
        medicine_column.pack(side="left", expand=True, fill="x", padx=8)
        ctk.CTkLabel(medicine_column, text="ยา").pack(anchor="w", pady=(0, 4))
        self.medicine_option = ctk.CTkOptionMenu(
            medicine_column,
            values=["เลือกประเภทยาก่อน"],
            height=36,
            command=self._on_medicine_selected,
        )
        self.medicine_option.pack(fill="x")

        value_column = ctk.CTkFrame(selectors, fg_color="transparent")
        value_column.pack(side="left", fill="x", padx=8)
        self.value_label = ctk.CTkLabel(value_column, text="จำนวนต่อครั้ง")
        self.value_label.pack(anchor="w", pady=(0, 4))
        self.value_entry = ctk.CTkEntry(
            value_column,
            placeholder_text="เช่น 1",
            width=110,
            height=36,
        )
        self.value_entry.pack(fill="x")

        food_column = ctk.CTkFrame(selectors, fg_color="transparent")
        food_column.pack(side="left", fill="x", padx=(8, 0))
        ctk.CTkLabel(food_column, text="เวลาอาหาร").pack(anchor="w", pady=(0, 4))
        self.food_option = ctk.CTkOptionMenu(
            food_column, values=list(FOOD_OPTIONS), width=130, height=36
        )
        self.food_option.pack(fill="x")

        periods = ctk.CTkFrame(self.add_frame, fg_color="transparent")
        periods.pack(fill="x", padx=14, pady=(0, 10))
        ctk.CTkLabel(periods, text="ช่วงเวลาที่ต้องกิน").pack(side="left", padx=(0, 8))
        self.time_vars = {}
        for time_id, label in TIME_PERIODS.items():
            variable = ctk.BooleanVar(value=False)
            self.time_vars[time_id] = variable
            ctk.CTkCheckBox(
                periods,
                text=label,
                variable=variable,
                checkbox_width=18,
                checkbox_height=18,
            ).pack(side="left", padx=8)

        self.add_button = ctk.CTkButton(
            self.add_frame,
            text="เพิ่มยา",
            height=36,
            command=self.add_medicine,
        )
        self.add_button.pack(anchor="e", padx=14, pady=(0, 12))
        self.busy_buttons.append(self.add_button)

        schedule_header = ctk.CTkFrame(content, fg_color="transparent")
        schedule_header.pack(fill="x", pady=(0, 6))
        ctk.CTkLabel(
            schedule_header,
            text="ตารางยาที่ต้องกินวันนี้",
            font=("Helvetica", 16, "bold"),
            text_color="#0F172A",
        ).pack(side="left")
        self.refresh_button = ctk.CTkButton(
            schedule_header,
            text="รีเฟรช",
            width=100,
            command=self.refresh,
        )
        self.refresh_button.pack(side="right")
        self.busy_buttons.append(self.refresh_button)

        self.schedule_list = ctk.CTkScrollableFrame(
            content, fg_color="transparent"
        )
        self.schedule_list.pack(fill="both", expand=True)
        self.refresh()

    def refresh(self):
        user_id = self.user.get("userId")
        if not isinstance(user_id, str) or not user_id:
            self._show_status("ไม่พบรหัสผู้ใช้สำหรับโหลดรายการยา", error=True)
            return
        query = urlencode({"user_id": user_id})
        requests = [
            ("/med/type", None, "GET"),
            ("/med", None, "GET"),
            (f"/user/med?{query}", None, "GET"),
        ]
        self._run_requests(requests, self._show_data, "กำลังโหลดข้อมูลยาของคุณ...")

    def _on_type_selected(self, selected_type):
        type_id = self.type_ids_by_name.get(selected_type)
        if type_id is None:
            self.medicines_by_label = {}
            self.medicine_option.configure(values=["ไม่พบประเภทยา"])
            self.medicine_option.set("ไม่พบประเภทยา")
            return
        medicines = [
            medicine
            for medicine in self.catalog_medicines
            if medicine.get("medTypeId") == type_id
        ]
        self.medicines_by_label = self._medicine_labels(medicines)
        labels = list(self.medicines_by_label) or ["ไม่มีรายการยาในประเภทนี้"]
        self.medicine_option.configure(values=labels)
        self.medicine_option.set(labels[0])
        self._on_medicine_selected(labels[0])

    def _on_medicine_selected(self, selected_medicine):
        medicine = self.medicines_by_label.get(selected_medicine)
        if medicine is None:
            self.value_label.configure(text="จำนวนต่อครั้ง")
            return
        unit = medicine.get("unitName")
        label = f"จำนวนต่อครั้ง ({unit})" if unit else "จำนวนต่อครั้ง"
        self.value_label.configure(text=label)

    @staticmethod
    def _medicine_labels(medicines):
        labels = {}
        for medicine in medicines:
            label = str(medicine.get("medName", "ไม่ระบุชื่อยา"))
            if label in labels:
                label = f"{label} · {medicine.get('medId', '')[:8]}"
            labels[label] = medicine
        return labels

    def add_medicine(self):
        if self.is_busy:
            return
        selected_medicine = self.medicines_by_label.get(self.medicine_option.get())
        value_text = self.value_entry.get().strip()
        times_per_day = [
            time_id
            for time_id, variable in self.time_vars.items()
            if variable.get()
        ]
        if selected_medicine is None:
            self._show_status("กรุณาเลือกยา", error=True)
            return
        if not value_text:
            self._show_status("กรุณากรอกจำนวนยาต่อครั้ง", error=True)
            return
        try:
            value = float(value_text)
        except ValueError:
            self._show_status("จำนวนยาต้องเป็นตัวเลขมากกว่า 0", error=True)
            return
        if not math.isfinite(value) or value <= 0:
            self._show_status("จำนวนยาต้องมากกว่า 0", error=True)
            return
        if not times_per_day:
            self._show_status("กรุณาเลือกช่วงเวลาที่ต้องกินยา", error=True)
            return

        if value.is_integer():
            value = int(value)
        payload = {
            "userId": self.user["userId"],
            "medId": selected_medicine["medId"],
            "value": value,
            "timesPerDay": times_per_day,
            "foodRequire": FOOD_OPTIONS[self.food_option.get()],
        }
        self._run_requests(
            [("/user/med", payload, "POST")],
            self._medicine_added,
            "กำลังเพิ่มยา...",
        )

    def _medicine_added(self, _responses):
        self.value_entry.delete(0, "end")
        for variable in self.time_vars.values():
            variable.set(False)
        self.food_option.set("ไม่ระบุ")
        self._show_status("เพิ่มยาในรายการของคุณแล้ว")
        self.refresh()

    def _delete_medicine(self, user_medicine, medicine_name):
        if self.is_busy:
            return
        if not messagebox.askyesno(
            "ยืนยันการลบ",
            f"นำ “{medicine_name}” ออกจากรายการยาของคุณหรือไม่?",
            parent=self,
        ):
            return
        payload = {
            "userId": self.user["userId"],
            "medId": user_medicine["medId"],
        }
        self._run_requests(
            [("/user/med", payload, "DELETE")],
            self._medicine_deleted,
            "กำลังนำยาออกจากรายการ...",
        )

    def _medicine_deleted(self, _responses):
        self._show_status("นำยาออกจากรายการแล้ว")
        self.refresh()

    def _run_requests(self, requests, on_success, loading_message):
        if self.is_busy:
            return
        self.is_busy = True
        self._set_buttons_enabled(False)
        self._show_status(loading_message)
        self.loading_bar.pack(fill="x", pady=(0, 8))
        self.loading_bar.start()

        def worker():
            try:
                responses = [
                    self.api_request(path, payload, method=method)
                    for path, payload, method in requests
                ]
            except APIRequestError as error:
                self.after(0, self._request_failed, str(error))
                return
            self.after(0, self._request_succeeded, responses, on_success)

        threading.Thread(target=worker, daemon=True).start()

    def _request_failed(self, message):
        self._stop_loading()
        self.is_busy = False
        self._set_buttons_enabled(True)
        self._show_status(message, error=True)

    def _request_succeeded(self, responses, on_success):
        self._stop_loading()
        self.is_busy = False
        self._set_buttons_enabled(True)
        on_success(responses)

    def _set_buttons_enabled(self, enabled):
        state = "normal" if enabled else "disabled"
        for button in self.busy_buttons:
            button.configure(state=state)

    def _show_status(self, message, error=False):
        if self.error_after_id is not None:
            self.after_cancel(self.error_after_id)
            self.error_after_id = None
        self.status_label.configure(
            text=message,
            text_color="#B91C1C" if error else "#475569",
        )
        if error:
            self.error_after_id = self.after(3000, self._clear_error)

    def _clear_error(self):
        self.error_after_id = None
        self.status_label.configure(text="")

    def _stop_loading(self):
        self.loading_bar.stop()
        self.loading_bar.pack_forget()

    def _show_data(self, responses):
        types, medicines, user_medicines = responses
        if any(not isinstance(items, list) for items in responses):
            self._show_status("รูปแบบข้อมูลจาก API ไม่ถูกต้อง", error=True)
            return
        if any(
            not isinstance(item, dict)
            for items in responses
            for item in items
        ):
            self._show_status("รูปแบบข้อมูลจาก API ไม่ถูกต้อง", error=True)
            return

        self.medicine_types = types
        self.catalog_medicines = medicines
        self.user_medicines = user_medicines
        self.type_ids_by_name = {
            item["medTypeName"]: item["medTypeId"]
            for item in types
            if isinstance(item.get("medTypeName"), str)
            and isinstance(item.get("medTypeId"), str)
        }
        type_names = list(self.type_ids_by_name) or ["ยังไม่มีประเภทยา"]
        self.type_option.configure(values=type_names)
        self.type_option.set(type_names[0])
        self._on_type_selected(type_names[0])
        self._render_schedule()
        self._show_status("ข้อมูลยาของวันนี้")

    def _render_schedule(self):
        for child in self.schedule_list.winfo_children():
            child.destroy()

        medicines_by_id = {
            medicine.get("medId"): medicine
            for medicine in self.catalog_medicines
            if isinstance(medicine.get("medId"), str)
        }
        scheduled_by_time = {
            time_id: [
                user_medicine
                for user_medicine in self.user_medicines
                if time_id in user_medicine.get("timesPerDay", [])
            ]
            for time_id in TIME_PERIODS
        }
        ordered_periods = sorted(
            TIME_PERIODS.items(),
            key=lambda period: (
                not scheduled_by_time[period[0]],
                period[0],
            ),
        )
        for time_id, period_name in ordered_periods:
            section = ctk.CTkFrame(
                self.schedule_list, fg_color="#FFFFFF", corner_radius=12
            )
            section.pack(fill="x", pady=5)
            ctk.CTkLabel(
                section,
                text=period_name,
                font=("Helvetica", 14, "bold"),
                text_color="#0F766E",
            ).pack(anchor="w", padx=14, pady=(10, 4))

            scheduled = scheduled_by_time[time_id]
            if not scheduled:
                ctk.CTkLabel(
                    section, text="ไม่มีรายการยา", text_color="#94A3B8"
                ).pack(anchor="w", padx=14, pady=(0, 10))
                continue

            for user_medicine in scheduled:
                medicine = medicines_by_id.get(user_medicine.get("medId"), {})
                self._render_scheduled_medicine(section, medicine, user_medicine)

    def _render_scheduled_medicine(self, parent, medicine, user_medicine):
        row = ctk.CTkFrame(parent, fg_color="#F8FAFC", corner_radius=8)
        row.pack(fill="x", padx=10, pady=4)
        details = ctk.CTkFrame(row, fg_color="transparent")
        details.pack(side="left", fill="x", expand=True, padx=10, pady=8)
        medicine_name = medicine.get("medName", "ไม่พบข้อมูลยา")
        unit = medicine.get("unitName", "")
        amount = user_medicine.get("value")
        amount_text = f"{amount:g} {unit}".strip() if isinstance(amount, (int, float)) else unit
        food_require = user_medicine.get("foodRequire")
        food_text = {
            "before": "ก่อนอาหาร",
            "after": "หลังอาหาร",
        }.get(food_require)
        description = amount_text
        if food_text:
            description = f"{description} · {food_text}" if description else food_text
        ctk.CTkLabel(
            details,
            text=medicine_name,
            font=("Helvetica", 12, "bold"),
            text_color="#0F172A",
            anchor="w",
        ).pack(anchor="w")
        if description:
            ctk.CTkLabel(
                details,
                text=description,
                font=("Helvetica", 11),
                text_color="#64748B",
                anchor="w",
            ).pack(anchor="w", pady=(2, 0))
        ctk.CTkButton(
            row,
            text="ลบ",
            width=75,
            fg_color="#DC2626",
            hover_color="#B91C1C",
            command=lambda item=user_medicine, name=medicine_name: self._delete_medicine(
                item, name
            ),
        ).pack(side="right", padx=10, pady=8)

    def logout(self):
        if self.is_busy:
            return
        self._run_requests(
            [
                (
                    "/auth/logout",
                    {"userId": self.user.get("userId", "")},
                    "POST",
                )
            ],
            lambda _responses: self.on_logout(),
            "กำลังออกจากระบบ...",
        )
