import threading
from tkinter import messagebox

import customtkinter as ctk

from .api_client import APIRequestError


class AdminView(ctk.CTkFrame):
    def __init__(self, master, user, api_request, on_logout):
        super().__init__(master, fg_color="#F1F5F9")
        self.user = user
        self.api_request = api_request
        self.on_logout = on_logout
        self.medicines = []
        self.medicine_types = []
        self.type_names_by_id = {}
        self.busy_buttons = []
        self.is_busy = False
        self.error_after_id = None

        header = ctk.CTkFrame(self, fg_color="#0F172A", corner_radius=0, height=76)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(
            header,
            text="จัดการข้อมูลยาในระบบ",
            font=("Helvetica", 20, "bold"),
            text_color="#FFFFFF",
        ).pack(side="left", padx=24)
        ctk.CTkLabel(
            header,
            text=f"ผู้ดูแลระบบ: {user.get('userName', '-')}",
            font=("Helvetica", 12),
            text_color="#CBD5E1",
        ).pack(side="left", padx=12)
        self.logout_button = ctk.CTkButton(
            header,
            text="ออกจากระบบ",
            width=110,
            fg_color="#DC2626",
            hover_color="#B91C1C",
            command=self.logout,
        )
        self.logout_button.pack(side="right", padx=20)
        self.busy_buttons.append(self.logout_button)

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=14)

        toolbar = ctk.CTkFrame(content, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(
            toolbar,
            text="เพิ่มและลบข้อมูลผ่าน API ของระบบ",
            text_color="#475569",
        ).pack(side="left")
        self.refresh_button = ctk.CTkButton(
            toolbar, text="รีเฟรช", width=90, command=self.refresh
        )
        self.refresh_button.pack(side="right")
        self.busy_buttons.append(self.refresh_button)

        self.status_label = ctk.CTkLabel(
            content, text="", anchor="w", wraplength=800, text_color="#475569"
        )
        self.status_label.pack(fill="x", pady=(0, 6))
        self.loading_bar = ctk.CTkProgressBar(
            content, mode="indeterminate", height=4
        )

        self.tabs = ctk.CTkTabview(content)
        self.tabs.pack(fill="both", expand=True)
        self.medicine_tab = self.tabs.add("ข้อมูลยา")
        self.type_tab = self.tabs.add("ประเภทยา")
        self._build_medicine_tab()
        self._build_type_tab()
        self.refresh()

    def _build_medicine_tab(self):
        form = ctk.CTkFrame(self.medicine_tab, fg_color="#FFFFFF", corner_radius=12)
        form.pack(fill="x", padx=8, pady=(8, 12))

        fields = ctk.CTkFrame(form, fg_color="transparent")
        fields.pack(fill="x", padx=14, pady=(12, 4))

        name_column = ctk.CTkFrame(fields, fg_color="transparent")
        name_column.pack(side="left", expand=True, fill="x", padx=(0, 8))
        ctk.CTkLabel(name_column, text="ชื่อยา").pack(anchor="w", pady=(0, 4))
        self.medicine_name_entry = ctk.CTkEntry(
            name_column, placeholder_text="ชื่อยา", height=36
        )
        self.medicine_name_entry.pack(fill="x")

        type_column = ctk.CTkFrame(fields, fg_color="transparent")
        type_column.pack(side="left", expand=True, fill="x", padx=8)
        ctk.CTkLabel(type_column, text="ประเภทยา").pack(anchor="w", pady=(0, 4))
        self.type_option = ctk.CTkOptionMenu(
            type_column, values=["กำลังโหลด..."], height=36
        )
        self.type_option.pack(fill="x")

        unit_column = ctk.CTkFrame(fields, fg_color="transparent")
        unit_column.pack(side="left", expand=True, fill="x", padx=8)
        ctk.CTkLabel(unit_column, text="หน่วยนับ").pack(anchor="w", pady=(0, 4))
        self.unit_entry = ctk.CTkEntry(
            unit_column, placeholder_text="เช่น เม็ด, ช้อน, หยด", height=36
        )
        self.unit_entry.pack(fill="x")

        bud_column = ctk.CTkFrame(fields, fg_color="transparent")
        bud_column.pack(side="left", fill="x", padx=(8, 0))
        ctk.CTkLabel(bud_column, text="BUD (วัน, ไม่บังคับ)").pack(
            anchor="w", pady=(0, 4)
        )
        self.bud_entry = ctk.CTkEntry(
            bud_column, placeholder_text="เว้นว่างได้", width=100, height=36
        )
        self.bud_entry.pack(fill="x")

        self.add_medicine_button = ctk.CTkButton(
            form,
            text="เพิ่มยา",
            height=36,
            command=self.add_medicine,
        )
        self.add_medicine_button.pack(anchor="e", padx=14, pady=(6, 12))
        self.busy_buttons.append(self.add_medicine_button)

        self.medicine_list = ctk.CTkScrollableFrame(
            self.medicine_tab, fg_color="transparent"
        )
        self.medicine_list.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def _build_type_tab(self):
        form = ctk.CTkFrame(self.type_tab, fg_color="#FFFFFF", corner_radius=12)
        form.pack(fill="x", padx=8, pady=(8, 12))

        ctk.CTkLabel(form, text="ชื่อประเภทยา").pack(
            anchor="w", padx=14, pady=(12, 4)
        )
        self.type_name_entry = ctk.CTkEntry(
            form, placeholder_text="เช่น ยาแก้ปวด", height=36
        )
        self.type_name_entry.pack(fill="x", padx=14)

        self.add_type_button = ctk.CTkButton(
            form, text="เพิ่มประเภท", height=36, command=self.add_medicine_type
        )
        self.add_type_button.pack(anchor="e", padx=14, pady=12)
        self.busy_buttons.append(self.add_type_button)

        self.type_list = ctk.CTkScrollableFrame(
            self.type_tab, fg_color="transparent"
        )
        self.type_list.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def refresh(self):
        self._run_requests(
            [
                ("/med/type", None, "GET"),
                ("/med", None, "GET"),
            ],
            self._show_data,
            "กำลังโหลดข้อมูลยา...",
        )

    def add_medicine(self):
        if self.is_busy:
            return
        med_name = self.medicine_name_entry.get().strip()
        unit_name = self.unit_entry.get().strip()
        bud_text = self.bud_entry.get().strip()
        med_type_id = self.type_names_by_id.get(self.type_option.get())
        if not med_name or not unit_name or med_type_id is None:
            self._show_status("กรุณากรอกชื่อยา ประเภท และหน่วยนับ", error=True)
            return
        bud_value = None
        if bud_text and bud_text.lower() != "null":
            if not bud_text.isdigit():
                self._show_status(
                    "BUD ต้องเป็นจำนวนเต็มตั้งแต่ 0 ขึ้นไป หรือเว้นว่าง/พิมพ์ null",
                    error=True,
                )
                return
            bud_value = int(bud_text)

        payload = {
            "medName": med_name,
            "medTypeId": med_type_id,
            "unitName": unit_name,
            "BUD": bud_value,
        }
        self._run_requests(
            [("/med", payload, "POST")],
            self._medicine_added,
            "กำลังเพิ่มยา...",
        )

    def _medicine_added(self, _responses):
        self.medicine_name_entry.delete(0, "end")
        self.unit_entry.delete(0, "end")
        self.bud_entry.delete(0, "end")
        self._show_status("เพิ่มรายการยาแล้ว")
        self.refresh()

    def add_medicine_type(self):
        if self.is_busy:
            return
        type_name = self.type_name_entry.get().strip()
        if not type_name:
            self._show_status("กรุณากรอกชื่อประเภทยา", error=True)
            return
        self._run_requests(
            [("/med/type", {"medTypeName": type_name}, "POST")],
            self._type_added,
            "กำลังเพิ่มประเภทยา...",
        )

    def _type_added(self, _responses):
        self.type_name_entry.delete(0, "end")
        self._show_status("เพิ่มประเภทยาแล้ว")
        self.refresh()

    def _delete_medicine(self, medicine):
        if self.is_busy:
            return
        if not messagebox.askyesno(
            "ยืนยันการลบ",
            f"ต้องการลบยา “{medicine.get('medName', '')}” หรือไม่?",
            parent=self,
        ):
            return
        self._run_requests(
            [("/med", {"medId": medicine["medId"]}, "DELETE")],
            self._medicine_deleted,
            "กำลังลบยา...",
        )

    def _medicine_deleted(self, _responses):
        self._show_status("ลบรายการยาแล้ว")
        self.refresh()

    def _delete_medicine_type(self, medicine_type):
        if self.is_busy:
            return
        if not messagebox.askyesno(
            "ยืนยันการลบประเภทยา",
            "การลบประเภทอาจทำให้ยาเดิมที่อ้างอิงประเภทนี้ไม่แสดงชื่อประเภท "
            "ต้องการดำเนินการต่อหรือไม่?",
            parent=self,
        ):
            return
        self._run_requests(
            [
                (
                    "/med/type",
                    {"medTypeId": medicine_type["medTypeId"]},
                    "DELETE",
                )
            ],
            self._type_deleted,
            "กำลังลบประเภทยา...",
        )

    def _type_deleted(self, _responses):
        self._show_status("ลบประเภทยาแล้ว")
        self.refresh()

    def _run_requests(self, requests, on_success, loading_message):
        if self.is_busy:
            return
        self.is_busy = True
        self._set_buttons_enabled(False)
        self._show_status(loading_message)
        self._start_loading()

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

    def _start_loading(self):
        self.loading_bar.pack(fill="x", pady=(0, 8))
        self.loading_bar.start()

    def _stop_loading(self):
        self.loading_bar.stop()
        self.loading_bar.pack_forget()

    def _show_data(self, responses):
        types, medicines = responses
        if not isinstance(types, list) or not isinstance(medicines, list):
            self._show_status("รูปแบบข้อมูลจาก API ไม่ถูกต้อง", error=True)
            return
        if any(not isinstance(item, dict) for item in types + medicines):
            self._show_status("รูปแบบข้อมูลจาก API ไม่ถูกต้อง", error=True)
            return

        self.medicine_types = types
        self.medicines = medicines
        self.type_names_by_id = {
            item["medTypeName"]: item["medTypeId"]
            for item in types
            if isinstance(item.get("medTypeName"), str)
            and isinstance(item.get("medTypeId"), str)
        }
        type_names = list(self.type_names_by_id) or ["ยังไม่มีประเภทยา"]
        self.type_option.configure(values=type_names)
        self.type_option.set(type_names[0])
        self._render_types()
        self._render_medicines()
        self._show_status("โหลดข้อมูลยาแล้ว")

    def _render_types(self):
        for child in self.type_list.winfo_children():
            child.destroy()
        if not self.medicine_types:
            ctk.CTkLabel(
                self.type_list,
                text="ยังไม่มีประเภทยา",
                text_color="#64748B",
            ).pack(pady=18)
            return
        for medicine_type in self.medicine_types:
            row = ctk.CTkFrame(self.type_list, fg_color="#FFFFFF", corner_radius=10)
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(
                row,
                text=medicine_type.get("medTypeName", "-"),
                font=("Helvetica", 13, "bold"),
                text_color="#0F172A",
            ).pack(side="left", padx=14, pady=12)
            ctk.CTkButton(
                row,
                text="ลบ",
                width=64,
                fg_color="#DC2626",
                hover_color="#B91C1C",
                command=lambda item=medicine_type: self._delete_medicine_type(item),
            ).pack(side="right", padx=12, pady=8)

    def _render_medicines(self):
        for child in self.medicine_list.winfo_children():
            child.destroy()
        if not self.medicines:
            ctk.CTkLabel(
                self.medicine_list,
                text="ยังไม่มีรายการยา",
                text_color="#64748B",
            ).pack(pady=18)
            return
        for medicine in self.medicines:
            type_name = next(
                (
                    item.get("medTypeName", "ไม่พบประเภท")
                    for item in self.medicine_types
                    if item.get("medTypeId") == medicine.get("medTypeId")
                ),
                "ไม่พบประเภท",
            )
            row = ctk.CTkFrame(self.medicine_list, fg_color="#FFFFFF", corner_radius=10)
            row.pack(fill="x", pady=4)
            details = ctk.CTkFrame(row, fg_color="transparent")
            details.pack(side="left", fill="x", expand=True, padx=14, pady=9)
            ctk.CTkLabel(
                details,
                text=medicine.get("medName", "-"),
                font=("Helvetica", 13, "bold"),
                text_color="#0F172A",
                anchor="w",
            ).pack(anchor="w")
            ctk.CTkLabel(
                details,
                text=(
                    f"{type_name} · {medicine.get('unitName', '-')} · "
                    f"BUD {medicine['BUD']} วัน"
                    if medicine.get("BUD") is not None
                    else f"{type_name} · {medicine.get('unitName', '-')} · ไม่ระบุ BUD"
                ),
                font=("Helvetica", 11),
                text_color="#64748B",
                anchor="w",
            ).pack(anchor="w", pady=(2, 0))
            ctk.CTkButton(
                row,
                text="ลบ",
                width=64,
                fg_color="#DC2626",
                hover_color="#B91C1C",
                command=lambda item=medicine: self._delete_medicine(item),
            ).pack(side="right", padx=12, pady=8)

    def logout(self):
        if self.is_busy:
            return
        self.is_busy = True
        self._set_buttons_enabled(False)
        self._show_status("กำลังออกจากระบบ...")
        self._start_loading()

        def worker():
            try:
                self.api_request(
                    "/auth/logout",
                    {"userId": self.user.get("userId", "")},
                    method="POST",
                )
            except APIRequestError as error:
                self.after(0, self._logout_failed, str(error))
                return
            self.after(0, self.on_logout)

        threading.Thread(target=worker, daemon=True).start()

    def _logout_failed(self, message):
        self._stop_loading()
        self.is_busy = False
        self._set_buttons_enabled(True)
        self._show_status(f"ออกจากระบบไม่สำเร็จ: {message}", error=True)
