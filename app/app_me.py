import customtkinter as ctk

from .api_client import APIRequestError


class ProfileView(ctk.CTkFrame):
    def __init__(self, master, user, api_request, on_logout):
        super().__init__(master, fg_color="#F1F5F9")
        self.user = user
        self.api_request = api_request
        self.on_logout = on_logout

        card = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=16)
        card.pack(fill="both", expand=True, padx=32, pady=32)

        ctk.CTkLabel(
            card,
            text="ข้อมูลบัญชีของฉัน",
            font=("Helvetica", 22, "bold"),
            text_color="#0F172A",
        ).pack(anchor="w", padx=28, pady=(30, 20))

        details = ctk.CTkFrame(card, fg_color="#F8FAFC", corner_radius=12)
        details.pack(fill="x", padx=24, pady=(0, 16))

        self._add_detail(details, "ชื่อผู้ใช้", user.get("userName", "-"))
        self._add_detail(details, "รหัสผู้ใช้", user.get("userId", "-"))
        self._add_detail(details, "สิทธิ์การใช้งาน", user.get("userRole", "-"))

        self.status_label = ctk.CTkLabel(
            card, text="", text_color="#B91C1C", wraplength=320
        )
        self.status_label.pack(fill="x", padx=28, pady=(0, 8))

        ctk.CTkButton(
            card,
            text="ออกจากระบบ",
            height=42,
            corner_radius=8,
            fg_color="#DC2626",
            hover_color="#B91C1C",
            command=self.logout,
        ).pack(fill="x", padx=28, pady=(0, 28))

    @staticmethod
    def _add_detail(parent, label, value):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=10)
        ctk.CTkLabel(
            row, text=label, text_color="#64748B", font=("Helvetica", 12)
        ).pack(anchor="w")
        ctk.CTkLabel(
            row,
            text=str(value),
            text_color="#0F172A",
            font=("Helvetica", 14, "bold"),
            wraplength=300,
            justify="left",
        ).pack(anchor="w", pady=(3, 0))

    def logout(self):
        try:
            self.api_request("/auth/logout", {"userId": self.user.get("userId", "")})
        except APIRequestError as error:
            self.status_label.configure(
                text=f"ออกจากระบบในเครื่องแล้ว แต่แจ้งเซิร์ฟเวอร์ไม่สำเร็จ: {error}"
            )
        self.on_logout()
