import customtkinter as ctk

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class VibrantPatientApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ระบบลงทะเบียนผู้ป่วย - Patient Registration")
        self.geometry("480x610")
        self.resizable(False, False)
        self.configure(fg_color="#F1F5F9")  # พื้นหลังสี Slate อ่อน

        # ---------------- 1. Top Colorful Header Banner ----------------
        self.header_frame = ctk.CTkFrame(
            self,
            fg_color="#4F46E5",  # สี Indigo สดใส
            corner_radius=0,
            height=100
        )
        self.header_frame.pack(fill="x", side="top")
        self.header_frame.pack_propagate(False)

        self.header_title = ctk.CTkLabel(
            self.header_frame,
            text="🏥 ระบบลงทะเบียนผู้ป่วยใหม่",
            font=("Helvetica", 20, "bold"),
            text_color="#FFFFFF"
        )
        self.header_title.pack(anchor="w", padx=24, pady=(22, 2))

        self.header_subtitle = ctk.CTkLabel(
            self.header_frame,
            text="กรอกข้อมูลประวัติการรักษาและประวัติการแพ้ยาของผู้ป่วย",
            font=("Helvetica", 12),
            text_color="#C7D2FE"
        )
        self.header_subtitle.pack(anchor="w", padx=24)

        # ---------------- 2. Main Card Container ----------------
        self.card = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=18,
            border_width=0
        )
        self.card.pack(padx=20, pady=20, fill="both", expand=True)

        # ---------------- Form Fields ----------------
        # Field 1: ชื่อ-นามสกุล (แถบสีฟ้า Cyan)
        self.name_header = ctk.CTkFrame(self.card, fg_color="transparent")
        self.name_header.pack(anchor="w", padx=24, pady=(20, 4))
        
        ctk.CTkFrame(self.name_header, width=8, height=16, corner_radius=4, fg_color="#0EA5E9").pack(side="left", padx=(0, 8))
        ctk.CTkLabel(self.name_header, text="ชื่อ - นามสกุล", font=("Helvetica", 13, "bold"), text_color="#0F172A").pack(side="left")

        self.name_entry = ctk.CTkEntry(
            self.card,
            placeholder_text="เช่น นายสมชาย ใจดี",
            height=42,
            corner_radius=10,
            border_color="#38BDF8",
            border_width=1.5,
            fg_color="#F0F9FF"  # สีฟ้าพาสเทลอ่อน
        )
        self.name_entry.pack(fill="x", padx=24, pady=(0, 14))

        # Field 2: อายุ (แถบสีม่วง Violet)
        self.age_header = ctk.CTkFrame(self.card, fg_color="transparent")
        self.age_header.pack(anchor="w", padx=24, pady=(0, 4))
        
        ctk.CTkFrame(self.age_header, width=8, height=16, corner_radius=4, fg_color="#8B5CF6").pack(side="left", padx=(0, 8))
        ctk.CTkLabel(self.age_header, text="อายุ (ปี)", font=("Helvetica", 13, "bold"), text_color="#0F172A").pack(side="left")

        self.age_entry = ctk.CTkEntry(
            self.card,
            placeholder_text="เช่น 25",
            height=42,
            corner_radius=10,
            border_color="#C084FC",
            border_width=1.5,
            fg_color="#FAF5FF"  # สีม่วงพาสเทลอ่อน
        )
        self.age_entry.pack(fill="x", padx=24, pady=(0, 14))

        # Field 3: ประวัติการแพ้ยา (แถบสีส้ม Amber เตือนความสำคัญ)
        self.allergy_header = ctk.CTkFrame(self.card, fg_color="transparent")
        self.allergy_header.pack(anchor="w", padx=24, pady=(0, 4))
        
        ctk.CTkFrame(self.allergy_header, width=8, height=16, corner_radius=4, fg_color="#F59E0B").pack(side="left", padx=(0, 8))
        ctk.CTkLabel(self.allergy_header, text="ประวัติการแพ้ยา ⚠️", font=("Helvetica", 13, "bold"), text_color="#0F172A").pack(side="left")

        self.allergy_textbox = ctk.CTkTextbox(
            self.card,
            height=85,
            corner_radius=10,
            border_color="#FCD34D",
            border_width=1.5,
            fg_color="#FFFBEB"  # สีเหลือง/ส้มพาสเทลอ่อน
        )
        self.allergy_textbox.pack(fill="x", padx=24, pady=(0, 20))

        # ---------------- Action Buttons ----------------
        self.btn_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.btn_frame.pack(fill="x", padx=24, pady=(0, 20))

        # ปุ่มล้างข้อมูล (สี Coral / Rose)
        self.clear_btn = ctk.CTkButton(
            self.btn_frame,
            text="ล้างข้อมูล",
            fg_color="#FEE2E2",
            text_color="#DC2626",
            hover_color="#FCA5A5",
            height=44,
            corner_radius=10,
            font=("Helvetica", 13, "bold"),
            command=self.clear_form
        )
        self.clear_btn.pack(side="left", expand=True, fill="x", padx=(0, 8))

        # ปุ่มบันทึกข้อมูล (สีเขียว Emerald สดใส)
        self.save_btn = ctk.CTkButton(
            self.btn_frame,
            text="บันทึกข้อมูลผู้ป่วย",
            fg_color="#10B981",
            text_color="#FFFFFF",
            hover_color="#059669",
            height=44,
            corner_radius=10,
            font=("Helvetica", 13, "bold"),
            command=self.save_data
        )
        self.save_btn.pack(side="right", expand=True, fill="x", padx=(8, 0))

    def clear_form(self):
        self.name_entry.delete(0, "end")
        self.age_entry.delete(0, "end")
        self.allergy_textbox.delete("1.0", "end")

    def save_data(self):
        name = self.name_entry.get().strip()
        age = self.age_entry.get().strip()
        allergy = self.allergy_textbox.get("1.0", "end").strip()

        if not name or not age:
            self.show_dialog("แจ้งเตือน", "กรุณากรอกชื่อและอายุให้ครบถ้วน", is_error=True)
            return

        if not age.isdigit():
            self.show_dialog("แจ้งเตือน", "กรุณากรอกอายุเป็นตัวเลขเท่านั้น", is_error=True)
            return

        summary = f"บันทึกข้อมูลเรียบร้อยแล้ว!\n\n• ชื่อ: {name}\n• อายุ: {age} ปี\n• แพ้ยา: {allergy if allergy else 'ไม่มี'}"
        self.show_dialog("สำเร็จ", summary)
        self.clear_form()

    def show_dialog(self, title, message, is_error=False):
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("340x220")
        dialog.resizable(False, False)
        dialog.grab_set()

        bg_header = "#EF4444" if is_error else "#10B981"
        btn_hover = "#DC2626" if is_error else "#059669"

        # Banner ด้านบน Pop-up
        header = ctk.CTkFrame(dialog, fg_color=bg_header, height=42, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text=title, font=("Helvetica", 14, "bold"), text_color="#FFFFFF").pack(pady=8)

        content = ctk.CTkLabel(dialog, text=message, wraplength=300, font=("Helvetica", 12), justify="left")
        content.pack(expand=True, padx=20, pady=10)

        ok_btn = ctk.CTkButton(
            dialog,
            text="ตกลง",
            fg_color=bg_header,
            hover_color=btn_hover,
            width=110,
            corner_radius=8,
            command=dialog.destroy
        )
        ok_btn.pack(pady=(0, 16))

if __name__ == "__main__":
    app = VibrantPatientApp()
    app.mainloop()