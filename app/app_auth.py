import threading

import customtkinter as ctk

from .api_client import APIRequestError


class AuthView(ctk.CTkFrame):
    def __init__(self, master, api_request, on_authenticated):
        super().__init__(master, fg_color="#F1F5F9")
        self.api_request = api_request
        self.on_authenticated = on_authenticated
        self.mode = "login"
        self.error_after_id = None

        card = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=16)
        card.pack(fill="both", expand=True, padx=32, pady=32)

        ctk.CTkLabel(
            card,
            text="ระบบจัดการคลินิก",
            font=("Helvetica", 22, "bold"),
            text_color="#0F172A",
        ).pack(pady=(32, 4))
        ctk.CTkLabel(
            card,
            text="เข้าสู่ระบบหรือสร้างบัญชีผู้ใช้",
            font=("Helvetica", 13),
            text_color="#64748B",
        ).pack(pady=(0, 24))

        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="x", padx=28)

        ctk.CTkLabel(
            form,
            text="ชื่อผู้ใช้",
            font=("Helvetica", 12, "bold"),
            text_color="#334155",
        ).pack(anchor="w", pady=(0, 6))
        self.username_entry = ctk.CTkEntry(
            form, placeholder_text="ชื่อผู้ใช้", height=40, corner_radius=8
        )
        self.username_entry.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            form,
            text="รหัสผ่าน",
            font=("Helvetica", 12, "bold"),
            text_color="#334155",
        ).pack(anchor="w", pady=(0, 6))
        self.password_entry = ctk.CTkEntry(
            form,
            placeholder_text="รหัสผ่าน",
            show="*",
            height=40,
            corner_radius=8,
        )
        self.password_entry.pack(fill="x", pady=(0, 12))
        self.password_entry.bind("<Return>", lambda _: self.submit())

        self.status_label = ctk.CTkLabel(
            form, text="", text_color="#B91C1C", wraplength=320
        )
        self.status_label.pack(fill="x", pady=(0, 8))

        self.loading_bar = ctk.CTkProgressBar(form, mode="indeterminate", height=4)

        self.submit_button = ctk.CTkButton(
            form,
            text="เข้าสู่ระบบ",
            height=42,
            corner_radius=8,
            font=("Helvetica", 13, "bold"),
            command=self.submit,
        )
        self.submit_button.pack(fill="x", pady=(0, 12))

        self.mode_button = ctk.CTkButton(
            form,
            text="ยังไม่มีบัญชี? สมัครสมาชิก",
            fg_color="transparent",
            text_color="#2563EB",
            hover_color="#EFF6FF",
            command=self.toggle_mode,
        )
        self.mode_button.pack(fill="x", pady=(0, 20))

    def toggle_mode(self):
        if self.submit_button.cget("state") == "disabled":
            return
        self.mode = "signup" if self.mode == "login" else "login"
        if self.mode == "signup":
            self.submit_button.configure(text="สมัครสมาชิก")
            self.mode_button.configure(text="มีบัญชีอยู่แล้ว? เข้าสู่ระบบ")
        else:
            self.submit_button.configure(text="เข้าสู่ระบบ")
            self.mode_button.configure(text="ยังไม่มีบัญชี? สมัครสมาชิก")
        self._clear_error()

    def submit(self):
        user_name = self.username_entry.get().strip()
        password = self.password_entry.get()
        if not user_name or not password:
            self._show_error("กรุณากรอกชื่อผู้ใช้และรหัสผ่าน")
            return

        path = "/auth/signup" if self.mode == "signup" else "/auth/login"
        payload = {"userName": user_name, "userPassword": password}
        self._clear_error()
        self.submit_button.configure(state="disabled")
        self.mode_button.configure(state="disabled")
        self.username_entry.configure(state="disabled")
        self.password_entry.configure(state="disabled")
        self.loading_bar.pack(fill="x", pady=(0, 8))
        self.loading_bar.start()
        self.status_label.configure(text="กำลังเชื่อมต่อ...", text_color="#475569")

        threading.Thread(
            target=self._request_auth,
            args=(path, payload),
            daemon=True,
        ).start()

    def _request_auth(self, path, payload):
        try:
            user = self.api_request(path, payload)
        except APIRequestError as error:
            self.after(0, self._handle_auth_error, str(error))
            return

        self.after(0, self._handle_auth_success, user)

    def _stop_loading(self):
        self.loading_bar.stop()
        self.loading_bar.pack_forget()
        self.submit_button.configure(state="normal")
        self.mode_button.configure(state="normal")
        self.username_entry.configure(state="normal")
        self.password_entry.configure(state="normal")

    def _handle_auth_error(self, message):
        self._stop_loading()
        self._show_error(message)

    def _handle_auth_success(self, user):
        self._stop_loading()
        self._clear_error()
        self.password_entry.delete(0, "end")
        self.on_authenticated(user)

    def _show_error(self, message):
        self._clear_error()
        self.status_label.configure(text=message, text_color="#B91C1C")
        self.error_after_id = self.after(3000, self._clear_error)

    def _clear_error(self):
        if self.error_after_id is not None:
            self.after_cancel(self.error_after_id)
            self.error_after_id = None
        self.status_label.configure(text="")
