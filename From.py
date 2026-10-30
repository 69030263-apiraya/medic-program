import customtkinter as ctk

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# ---------------- ข้อมูลจำลองคลังยา ----------------
MEDICATIONS_DATA = [
    {"id": "MED-001", "name": "Paracetamol 500mg", "category": "ยาลดไข้/แก้ปวด", "stock": 150, "unit": "กล่อง", "min_stock": 20},
    {"id": "MED-002", "name": "Amoxicillin 500mg", "category": "ยาฆ่าเชื้อ", "stock": 8, "unit": "กล่อง", "min_stock": 15},
    {"id": "MED-003", "name": "Ibuprofen 400mg", "category": "ยาแก้ปวด/แก้อักเสบ", "stock": 0, "unit": "กล่อง", "min_stock": 10},
    {"id": "MED-004", "name": "Cetirizine 10mg", "category": "ยาแก้แพ้", "stock": 85, "unit": "แผง", "min_stock": 20},
    {"id": "MED-005", "name": "Omeprazole 20mg", "category": "ยารักษาโรคกระเพาะ", "stock": 5, "unit": "กล่อง", "min_stock": 10},
    {"id": "MED-006", "name": "NSS Saline 0.9% 500ml", "category": "น้ำเกลือ/เวชภัณฑ์", "stock": 42, "unit": "ขวด", "min_stock": 15},
]

class MainClinicApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ระบบบริหารจัดการคลินิก - Clinic Management System")
        self.geometry("1000x650")
        self.resizable(True, True)
        self.configure(fg_color="#F8FAFC")

        # Layout Config (Grid 1x2: Sidebar + Main Content)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ---------------- 1. Sidebar Navigation ----------------
        self.sidebar = ctk.CTkFrame(self, width=230, corner_radius=0, fg_color="#0F172A")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)

        # Sidebar Logo Header
        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="🏥 CLINIC SYSTEM",
            font=("Helvetica", 18, "bold"),
            text_color="#38BDF8"
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(24, 20), sticky="w")

        # Navigation Buttons
        self.btn_patient = ctk.CTkButton(
            self.sidebar,
            text="📝  ลงทะเบียนผู้ป่วย",
            font=("Helvetica", 13, "bold"),
            anchor="w",
            height=44,
            corner_radius=10,
            command=self.show_patient_page
        )
        self.btn_patient.grid(row=1, column=0, padx=16, pady=6, sticky="ew")

        self.btn_med = ctk.CTkButton(
            self.sidebar,
            text="💊  คลังยา (Medication)",
            font=("Helvetica", 13, "bold"),
            anchor="w",
            height=44,
            corner_radius=10,
            command=self.show_med_page
        )
        self.btn_med.grid(row=2, column=0, padx=16, pady=6, sticky="ew")

        # Dark/Light Mode Switch
        self.theme_menu = ctk.CTkOptionMenu(
            self.sidebar,
            values=["Light", "Dark"],
            fg_color="#334155",
            button_color="#475569",
            height=32,
            command=self.change_theme
        )
        self.theme_menu.grid(row=5, column=0, padx=16, pady=20, sticky="ew")

        # ---------------- 2. Create Pages ----------------
        self.patient_frame = self.create_patient_page()
        self.med_frame = self.create_med_page()

        # แสดงหน้าเริ่มต้น (ลงทะเบียนผู้ป่วย)
        self.show_patient_page()

    # --- Switch Page Logic ---
    def set_nav_state(self, active_btn, inactive_btn):
        active_btn.configure(fg_color="#0EA5E9", hover_color="#0284C7", text_color="#FFFFFF")
        inactive_btn.configure(fg_color="transparent", hover_color="#1E293B", text_color="#94A3B8")

    def show_patient_page(self):
        self.med_frame.grid_forget()
        self.patient_frame.grid(row=0, column=1, sticky="nsew", padx=24, pady=24)
        self.set_nav_state(self.btn_patient, self.btn_med)

    def show_med_page(self):
        self.patient_frame.grid_forget()
        self.med_frame.grid(row=0, column=1, sticky="nsew", padx=24, pady=24)
        self.set_nav_state(self.btn_med, self.btn_patient)

    def change_theme(self, mode):
        ctk.set_appearance_mode(mode)

    # ==================== PAGE 1: PATIENT REGISTRATION ====================
    def create_patient_page(self):
        frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=16)

        # Header Banner
        header = ctk.CTkFrame(frame, fg_color="#4F46E5", corner_radius=12, height=85)
        header.pack(fill="x", padx=16, pady=16)
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="📝 ลงทะเบียนผู้ป่วยใหม่", font=("Helvetica", 18, "bold"), text_color="#FFFFFF").pack(anchor="w", padx=20, pady=(18, 2))
        ctk.CTkLabel(header, text="กรอกข้อมูลประวัติส่วนตัวและประวัติการแพ้ยาของผู้ป่วย", font=("Helvetica", 12), text_color="#C7D2FE").pack(anchor="w", padx=20)

        # Form Fields Container
        form = ctk.CTkFrame(frame, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=24, pady=10)

        # 1. Name
        ctk.CTkLabel(form, text="ชื่อ - นามสกุล", font=("Helvetica", 13, "bold"), text_color="#0F172A").pack(anchor="w", pady=(10, 4))
        self.patient_name = ctk.CTkEntry(form, placeholder_text="เช่น นายสมชาย ใจดี", height=42, corner_radius=8, fg_color="#F8FAFC", border_color="#38BDF8")
        self.patient_name.pack(fill="x", pady=(0, 14))

        # 2. Age
        ctk.CTkLabel(form, text="อายุ (ปี)", font=("Helvetica", 13, "bold"), text_color="#0F172A").pack(anchor="w", pady=(0, 4))
        self.patient_age = ctk.CTkEntry(form, placeholder_text="เช่น 25", height=42, corner_radius=8, fg_color="#F8FAFC", border_color="#C084FC")
        self.patient_age.pack(fill="x", pady=(0, 14))

        # 3. Allergy
        ctk.CTkLabel(form, text="ประวัติการแพ้ยา ⚠️", font=("Helvetica", 13, "bold"), text_color="#0F172A").pack(anchor="w", pady=(0, 4))
        self.patient_allergy = ctk.CTkTextbox(form, height=90, corner_radius=8, fg_color="#FFFBEB", border_color="#FCD34D", border_width=1)
        self.patient_allergy.pack(fill="x", pady=(0, 20))

        # Buttons
        btn_box = ctk.CTkFrame(form, fg_color="transparent")
        btn_box.pack(fill="x", pady=(10, 0))

        ctk.CTkButton(btn_box, text="ล้างข้อมูล", fg_color="#FEE2E2", text_color="#DC2626", hover_color="#FCA5A5", height=42, corner_radius=8, font=("Helvetica", 13, "bold"), command=self.clear_patient_form).pack(side="left", expand=True, fill="x", padx=(0, 8))
        ctk.CTkButton(btn_box, text="บันทึกข้อมูลผู้ป่วย", fg_color="#10B981", hover_color="#059669", height=42, corner_radius=8, font=("Helvetica", 13, "bold"), command=self.save_patient_form).pack(side="right", expand=True, fill="x", padx=(8, 0))

        return frame

    def clear_patient_form(self):
        self.patient_name.delete(0, "end")
        self.patient_age.delete(0, "end")
        self.patient_allergy.delete("1.0", "end")

    def save_patient_form(self):
        name = self.patient_name.get().strip()
        age = self.patient_age.get().strip()
        allergy = self.patient_allergy.get("1.0", "end").strip()

        if not name or not age:
            self.show_dialog("แจ้งเตือน", "กรุณากรอกชื่อและอายุให้ครบถ้วน", is_error=True)
            return

        if not age.isdigit():
            self.show_dialog("แจ้งเตือน", "กรุณากรอกอายุเป็นตัวเลขเท่านั้น", is_error=True)
            return

        summary = f"บันทึกข้อมูลเรียบร้อยแล้ว!\n\n• ชื่อ: {name}\n• อายุ: {age} ปี\n• ประวัติแพ้ยา: {allergy if allergy else 'ไม่มี'}"
        self.show_dialog("สำเร็จ", summary)
        self.clear_patient_form()

    # ==================== PAGE 2: MEDICATION INVENTORY ====================
    def create_med_page(self):
        frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=16)

        # Header Banner
        header = ctk.CTkFrame(frame, fg_color="#0D9488", corner_radius=12, height=85)
        header.pack(fill="x", padx=16, pady=16)
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="💊 ระบบจัดการคลังยา (Medication Inventory)", font=("Helvetica", 18, "bold"), text_color="#FFFFFF").pack(anchor="w", padx=20, pady=(18, 2))
        ctk.CTkLabel(header, text="รายการยาคงคลัง ตรวจสอบสถานะสต็อก และปรับปรุงจำนวนยา", font=("Helvetica", 12), text_color="#CCFBF1").pack(anchor="w", padx=20)

        # Controls (Search)
        ctrl = ctk.CTkFrame(frame, fg_color="transparent")
        ctrl.pack(fill="x", padx=16, pady=(0, 10))

        self.search_entry = ctk.CTkEntry(ctrl, placeholder_text="🔍 ค้นหาชื่อยา หรือรหัสยา...", width=280, height=38, corner_radius=8)
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.filter_meds)

        # Table Header
        th = ctk.CTkFrame(frame, fg_color="#F1F5F9", height=36, corner_radius=6)
        th.pack(fill="x", padx=16, pady=(0, 6))

        headers = [("รหัส/ชื่อยา", 210), ("หมวดหมู่", 140), ("คงเหลือ", 100), ("สถานะ", 90), ("การจัดการ", 80)]
        for text, width in headers:
            ctk.CTkLabel(th, text=text, font=("Helvetica", 12, "bold"), text_color="#475569", width=width, anchor="w").pack(side="left", padx=8)

        # Scrollable Cards Container
        self.med_scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        self.med_scroll.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self.med_list = MEDICATIONS_DATA.copy()
        self.render_med_list(self.med_list)

        return frame

    def render_med_list(self, items):
        for w in self.med_scroll.winfo_children():
            w.destroy()

        if not items:
            ctk.CTkLabel(self.med_scroll, text="ไม่พบรายการยาที่ค้นหา", font=("Helvetica", 13), text_color="#94A3B8").pack(pady=30)
            return

        for item in items:
            card = ctk.CTkFrame(self.med_scroll, fg_color="#F8FAFC", corner_radius=8, height=55, border_width=1, border_color="#E2E8F0")
            card.pack(fill="x", pady=3)

            # Drug Info
            info = ctk.CTkFrame(card, fg_color="transparent", width=210)
            info.pack(side="left", padx=8)
            ctk.CTkLabel(info, text=item["name"], font=("Helvetica", 12, "bold"), text_color="#0F172A", anchor="w").pack(anchor="w")
            ctk.CTkLabel(info, text=f"รหัส: {item['id']}", font=("Helvetica", 10), text_color="#64748B", anchor="w").pack(anchor="w")

            # Category & Stock
            ctk.CTkLabel(card, text=item["category"], font=("Helvetica", 11), text_color="#334155", width=140, anchor="w").pack(side="left", padx=8)
            ctk.CTkLabel(card, text=f"{item['stock']} {item['unit']}", font=("Helvetica", 12, "bold"), text_color="#0F172A", width=100, anchor="w").pack(side="left", padx=8)

            # Badge Status
            if item["stock"] <= 0:
                st_bg, st_fg, st_txt = "#FEE2E2", "#B91C1C", "หมดสต็อก"
            elif item["stock"] <= item["min_stock"]:
                st_bg, st_fg, st_txt = "#FEF3C7", "#B45309", "สต็อกต่ำ"
            else:
                st_bg, st_fg, st_txt = "#DCFCE7", "#15803D", "พร้อมจ่าย"

            badge = ctk.CTkFrame(card, fg_color=st_bg, corner_radius=10, width=80, height=24)
            badge.pack(side="left", padx=8)
            badge.pack_propagate(False)
            ctk.CTkLabel(badge, text=st_txt, font=("Helvetica", 10, "bold"), text_color=st_fg).pack(expand=True)

            # Edit Button
            ctk.CTkButton(
                card, 
                text="ปรับสต็อก", 
                width=70, 
                height=28, 
                fg_color="#2563EB", 
                hover_color="#1D4ED8", 
                corner_radius=6, 
                font=("Helvetica", 11),
                command=lambda i=item: self.edit_stock_dialog(i)
            ).pack(side="left", padx=8)

    def filter_meds(self, event=None):
        q = self.search_entry.get().strip().lower()
        filtered = [m for m in self.med_list if q in m["name"].lower() or q in m["id"].lower()]
        self.render_med_list(filtered)

    def edit_stock_dialog(self, item):
        dialog = ctk.CTkToplevel(self)
        dialog.title("ปรับจำนวนสต็อก")
        dialog.geometry("300x180")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=f"ปรับสต็อก: {item['name']}", font=("Helvetica", 13, "bold")).pack(pady=(16, 8))
        entry = ctk.CTkEntry(dialog, width=180)
        entry.insert(0, str(item["stock"]))
        entry.pack(pady=8)

        def update():
            if entry.get().strip().isdigit():
                item["stock"] = int(entry.get().strip())
                self.filter_meds()
                dialog.destroy()

        ctk.CTkButton(dialog, text="ตกลง", fg_color="#10B981", width=180, command=update).pack(pady=10)

    # ==================== COMMON DIALOG ====================
    def show_dialog(self, title, message, is_error=False):
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("320x200")
        dialog.grab_set()

        clr = "#EF4444" if is_error else "#10B981"
        hdr = ctk.CTkFrame(dialog, fg_color=clr, height=38, corner_radius=0)
        hdr.pack(fill="x")
        ctk.CTkLabel(hdr, text=title, font=("Helvetica", 13, "bold"), text_color="#FFFFFF").pack(pady=8)

        ctk.CTkLabel(dialog, text=message, font=("Helvetica", 12), wraplength=280).pack(expand=True, padx=16, pady=10)
        ctk.CTkButton(dialog, text="ตกลง", fg_color=clr, width=110, corner_radius=6, command=dialog.destroy).pack(pady=(0, 16))

if __name__ == "__main__":
    app = MainClinicApp()
    app.mainloop()