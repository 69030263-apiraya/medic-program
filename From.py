import customtkinter as ctk
from tkinter import messagebox

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# ---------------- ข้อมูลจำลองคลังยา (โครงสร้างข้อมูลแบบสมบูรณ์) ----------------
MEDICATIONS_DATA = [
    {
        "id": "MED-001",
        "name": "Paracetamol 500mg",
        "properties": "ลดไข้ บรรเทาปวดระดับน้อยถึงปานกลาง",
        "stock": 150,
        "unit": "เม็ด",
        "timing": "หลังอาหาร (ทันที)",
        "exp_date": "2027-12-31",
        "min_stock": 20
    },
    {
        "id": "MED-002",
        "name": "Amoxicillin 500mg",
        "properties": "ยาปฏิชีวนะ รักษาการติดเชื้อแบคทีเรีย",
        "stock": 8,
        "unit": "แคปซูล",
        "timing": "ก่อนอาหาร (30 นาที)",
        "exp_date": "2026-11-15",
        "min_stock": 15
    },
    {
        "id": "MED-003",
        "name": "Omeprazole 20mg",
        "properties": "ยาลดการหลั่งกรดในกระเพาะอาหาร",
        "stock": 0,
        "unit": "เม็ด",
        "timing": "ก่อนอาหาร (30 นาที)",
        "exp_date": "2026-08-20",
        "min_stock": 10
    }
]

# ==================== POPUP DIALOG: ฟอร์ม เพิ่ม/แก้ไข รายการยา ====================
class MedicationFormDialog(ctk.CTkToplevel):
    def __init__(self, parent, title="รายการยา", item=None, on_save_callback=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("460x620")
        self.resizable(False, False)
        self.grab_set()

        self.item = item
        self.on_save_callback = on_save_callback

        # Header Banner
        header_color = "#0284C7" if item else "#10B981"
        header = ctk.CTkFrame(self, fg_color=header_color, height=60, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        header_txt = "✏️ แก้ไขข้อมูลยา" if item else "➕ เพิ่มรายการยาใหม่"
        ctk.CTkLabel(header, text=header_txt, font=("Helvetica", 16, "bold"), text_color="#FFFFFF").pack(pady=16)

        # Form Content
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=24, pady=16)

        # 1. ชื่อยา
        ctk.CTkLabel(body, text="ชื่อยา / ขนาดความแรง *", font=("Helvetica", 12, "bold"), text_color="#0F172A").pack(anchor="w", pady=(0, 2))
        self.entry_name = ctk.CTkEntry(body, placeholder_text="เช่น Paracetamol 500mg", height=38, corner_radius=8)
        self.entry_name.pack(fill="x", pady=(0, 10))

        # 2. สรรพคุณ
        ctk.CTkLabel(body, text="สรรพคุณ / ข้อบ่งใช้", font=("Helvetica", 12, "bold"), text_color="#0F172A").pack(anchor="w", pady=(0, 2))
        self.txt_properties = ctk.CTkTextbox(body, height=60, corner_radius=8, fg_color="#F8FAFC", border_color="#CBD5E1", border_width=1)
        self.txt_properties.pack(fill="x", pady=(0, 10))

        # 3. จำนวนคงเหลือ & หน่วยนับ
        stock_frame = ctk.CTkFrame(body, fg_color="transparent")
        stock_frame.pack(fill="x", pady=(0, 10))

        col1 = ctk.CTkFrame(stock_frame, fg_color="transparent")
        col1.pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkLabel(col1, text="จำนวนคงเหลือ *", font=("Helvetica", 12, "bold"), text_color="#0F172A").pack(anchor="w", pady=(0, 2))
        self.entry_stock = ctk.CTkEntry(col1, placeholder_text="เช่น 100", height=38, corner_radius=8)
        self.entry_stock.pack(fill="x")

        col2 = ctk.CTkFrame(stock_frame, fg_color="transparent")
        col2.pack(side="right", expand=True, fill="x", padx=(6, 0))
        ctk.CTkLabel(col2, text="หน่วยนับ", font=("Helvetica", 12, "bold"), text_color="#0F172A").pack(anchor="w", pady=(0, 2))
        self.entry_unit = ctk.CTkEntry(col2, placeholder_text="เช่น เม็ด, กล่อง", height=38, corner_radius=8)
        self.entry_unit.pack(fill="x")

        # 4. วิธีทาน (ก่อน/หลังอาหาร)
        ctk.CTkLabel(body, text="วิธีรับประทาน", font=("Helvetica", 12, "bold"), text_color="#0F172A").pack(anchor="w", pady=(0, 2))
        self.opt_timing = ctk.CTkOptionMenu(
            body,
            values=["หลังอาหาร (ทันที)", "ก่อนอาหาร (30 นาที)", "พร้อมอาหาร", "ก่อนนอน", "ใช้เฉพาะเวลาปวด/มีอาการ"],
            height=38,
            corner_radius=8,
            fg_color="#F1F5F9",
            text_color="#0F172A",
            button_color="#CBD5E1",
            button_hover_color="#94A3B8"
        )
        self.opt_timing.pack(fill="x", pady=(0, 10))

        # 5. วันหมดอายุ
        ctk.CTkLabel(body, text="วันหมดอายุ (EXP)", font=("Helvetica", 12, "bold"), text_color="#0F172A").pack(anchor="w", pady=(0, 2))
        self.entry_exp = ctk.CTkEntry(body, placeholder_text="YYYY-MM-DD (เช่น 2027-12-31)", height=38, corner_radius=8)
        self.entry_exp.pack(fill="x", pady=(0, 16))

        # Action Buttons
        btn_box = ctk.CTkFrame(body, fg_color="transparent")
        btn_box.pack(fill="x")

        ctk.CTkButton(btn_box, text="ยกเลิก", fg_color="#F1F5F9", text_color="#475569", hover_color="#E2E8F0", height=40, corner_radius=8, command=self.destroy).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkButton(btn_box, text="บันทึกข้อมูล", fg_color=header_color, hover_color="#059669", height=40, corner_radius=8, font=("Helvetica", 12, "bold"), command=self.save).pack(side="right", expand=True, fill="x", padx=(6, 0))

        if self.item:
            self.load_item_data()

    def load_item_data(self):
        self.entry_name.insert(0, self.item["name"])
        self.txt_properties.insert("1.0", self.item.get("properties", ""))
        self.entry_stock.insert(0, str(self.item["stock"]))
        self.entry_unit.insert(0, self.item.get("unit", "หน่วย"))
        self.opt_timing.set(self.item.get("timing", "หลังอาหาร (ทันที)"))
        self.entry_exp.insert(0, self.item.get("exp_date", ""))

    def save(self):
        name = self.entry_name.get().strip()
        properties = self.txt_properties.get("1.0", "end").strip()
        stock = self.entry_stock.get().strip()
        unit = self.entry_unit.get().strip() or "หน่วย"
        timing = self.opt_timing.get()
        exp_date = self.entry_exp.get().strip()

        if not name or not stock:
            messagebox.showwarning("เตือน", "กรุณากรอกชื่อยาและจำนวนคงเหลือ")
            return

        if not stock.isdigit():
            messagebox.showwarning("เตือน", "จำนวนคงเหลือต้องเป็นตัวเลขเท่านั้น")
            return

        data = {
            "name": name,
            "properties": properties,
            "stock": int(stock),
            "unit": unit,
            "timing": timing,
            "exp_date": exp_date if exp_date else "ไม่ระบุ",
            "min_stock": 10
        }

        if self.on_save_callback:
            self.on_save_callback(data, self.item)

        self.destroy()

# ==================== MAIN CLINIC APPLICATION ====================
class MainClinicApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ระบบบริหารจัดการคลินิก - Clinic Management System")
        self.geometry("1050x680")
        self.configure(fg_color="#F8FAFC")

        self.medications = MEDICATIONS_DATA.copy()

        # Grid Layout (Sidebar + Main View)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ---------------- 1. Sidebar Menu ----------------
        self.sidebar = ctk.CTkFrame(self, width=230, corner_radius=0, fg_color="#0F172A")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="🏥 CLINIC SYSTEM",
            font=("Helvetica", 18, "bold"),
            text_color="#38BDF8"
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(24, 20), sticky="w")

        # Sidebar Buttons
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

        # Theme Switcher
        self.theme_menu = ctk.CTkOptionMenu(
            self.sidebar,
            values=["Light", "Dark"],
            fg_color="#334155",
            button_color="#475569",
            height=32,
            command=lambda mode: ctk.set_appearance_mode(mode)
        )
        self.theme_menu.grid(row=5, column=0, padx=16, pady=20, sticky="ew")

        # ---------------- 2. Pages Setup ----------------
        self.patient_frame = self.create_patient_page()
        self.med_frame = self.create_med_page()

        self.show_patient_page()

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

    # ==================== PAGE 1: PATIENT REGISTRATION ====================
    def create_patient_page(self):
        frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=16)

        header = ctk.CTkFrame(frame, fg_color="#4F46E5", corner_radius=12, height=85)
        header.pack(fill="x", padx=16, pady=16)
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="📝 ลงทะเบียนผู้ป่วยใหม่", font=("Helvetica", 18, "bold"), text_color="#FFFFFF").pack(anchor="w", padx=20, pady=(18, 2))
        ctk.CTkLabel(header, text="กรอกข้อมูลประวัติส่วนตัวและประวัติการแพ้ยาของผู้ป่วย", font=("Helvetica", 12), text_color="#C7D2FE").pack(anchor="w", padx=20)

        form = ctk.CTkFrame(frame, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=24, pady=10)

        ctk.CTkLabel(form, text="ชื่อ - นามสกุล", font=("Helvetica", 13, "bold"), text_color="#0F172A").pack(anchor="w", pady=(10, 4))
        self.patient_name = ctk.CTkEntry(form, placeholder_text="เช่น นายสมชาย ใจดี", height=42, corner_radius=8, fg_color="#F8FAFC", border_color="#38BDF8")
        self.patient_name.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(form, text="อายุ (ปี)", font=("Helvetica", 13, "bold"), text_color="#0F172A").pack(anchor="w", pady=(0, 4))
        self.patient_age = ctk.CTkEntry(form, placeholder_text="เช่น 25", height=42, corner_radius=8, fg_color="#F8FAFC", border_color="#C084FC")
        self.patient_age.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(form, text="ประวัติการแพ้ยา ⚠️", font=("Helvetica", 13, "bold"), text_color="#0F172A").pack(anchor="w", pady=(0, 4))
        self.patient_allergy = ctk.CTkTextbox(form, height=90, corner_radius=8, fg_color="#FFFBEB", border_color="#FCD34D", border_width=1)
        self.patient_allergy.pack(fill="x", pady=(0, 20))

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
            messagebox.showwarning("แจ้งเตือน", "กรุณากรอกชื่อและอายุให้ครบถ้วน")
            return

        if not age.isdigit():
            messagebox.showwarning("แจ้งเตือน", "กรุณากรอกอายุเป็นตัวเลขเท่านั้น")
            return

        summary = f"บันทึกข้อมูลเรียบร้อยแล้ว!\n\n• ชื่อ: {name}\n• อายุ: {age} ปี\n• ประวัติแพ้ยา: {allergy if allergy else 'ไม่มี'}"
        messagebox.showinfo("สำเร็จ", summary)
        self.clear_patient_form()

    # ==================== PAGE 2: MEDICATION INVENTORY (FULL CRUD) ====================
    def create_med_page(self):
        frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=16)

        header = ctk.CTkFrame(frame, fg_color="#0D9488", corner_radius=12, height=85)
        header.pack(fill="x", padx=16, pady=16)
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="💊 ระบบจัดการคลังยา (Medication Management)", font=("Helvetica", 18, "bold"), text_color="#FFFFFF").pack(anchor="w", padx=20, pady=(18, 2))
        ctk.CTkLabel(header, text="จัดการ เพิ่ม แก้ไข ลบ รายการยา สรรพคุณ และตรวจสอบวันหมดอายุ", font=("Helvetica", 12), text_color="#CCFBF1").pack(anchor="w", padx=20)

        # Control Bar
        ctrl = ctk.CTkFrame(frame, fg_color="transparent")
        ctrl.pack(fill="x", padx=16, pady=(0, 10))

        self.search_entry = ctk.CTkEntry(ctrl, placeholder_text="🔍 ค้นหาชื่อยา หรือสรรพคุณ...", width=300, height=38, corner_radius=8)
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", self.filter_meds)

        ctk.CTkButton(
            ctrl,
            text="+ เพิ่มรายการยาใหม่",
            fg_color="#10B981",
            hover_color="#059669",
            height=38,
            corner_radius=8,
            font=("Helvetica", 12, "bold"),
            command=self.open_add_dialog
        ).pack(side="right")

        # Scrollable Cards Container
        self.med_scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        self.med_scroll.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self.render_med_cards(self.medications)

        return frame

    def render_med_cards(self, items):
        for w in self.med_scroll.winfo_children():
            w.destroy()

        if not items:
            ctk.CTkLabel(self.med_scroll, text="ไม่พบรายการยาที่ค้นหา", font=("Helvetica", 13), text_color="#94A3B8").pack(pady=40)
            return

        for item in items:
            card = ctk.CTkFrame(self.med_scroll, fg_color="#FFFFFF", corner_radius=12, border_width=1, border_color="#E2E8F0")
            card.pack(fill="x", pady=5, padx=2)

            main_box = ctk.CTkFrame(card, fg_color="transparent")
            main_box.pack(fill="x", padx=16, pady=12)

            # Left Info Column
            left_info = ctk.CTkFrame(main_box, fg_color="transparent")
            left_info.pack(side="left", expand=True, fill="x")

            top_line = ctk.CTkFrame(left_info, fg_color="transparent")
            top_line.pack(fill="x", anchor="w")

            ctk.CTkLabel(top_line, text=item["name"], font=("Helvetica", 14, "bold"), text_color="#0F172A").pack(side="left")

            # Status Badge (ตามสต็อก)
            if item["stock"] <= 0:
                st_bg, st_fg, st_txt = "#FEE2E2", "#B91C1C", "หมดสต็อก"
            elif item["stock"] <= item["min_stock"]:
                st_bg, st_fg, st_txt = "#FEF3C7", "#B45309", "สต็อกต่ำ"
            else:
                st_bg, st_fg, st_txt = "#DCFCE7", "#15803D", "พร้อมจ่าย"

            status_badge = ctk.CTkFrame(top_line, fg_color=st_bg, corner_radius=6)
            status_badge.pack(side="left", padx=8)
            ctk.CTkLabel(status_badge, text=st_txt, font=("Helvetica", 10, "bold"), text_color=st_fg).pack(padx=6, pady=2)

            # EXP Badge
            exp_badge = ctk.CTkFrame(top_line, fg_color="#F1F5F9", corner_radius=6)
            exp_badge.pack(side="left", padx=4)
            ctk.CTkLabel(exp_badge, text=f"EXP: {item.get('exp_date', 'N/A')}", font=("Helvetica", 10, "bold"), text_color="#475569").pack(padx=6, pady=2)

            # Properties & Usage Info
            ctk.CTkLabel(left_info, text=f"สรรพคุณ: {item.get('properties', '-')}", font=("Helvetica", 11), text_color="#64748B", anchor="w").pack(fill="x", pady=(2, 4))
            
            details = f"🍽️ วิธีทาน: {item.get('timing', '-')}   |   📦 สต็อก: {item['stock']} {item.get('unit', 'หน่วย')}"
            ctk.CTkLabel(left_info, text=details, font=("Helvetica", 11, "bold"), text_color="#0369A1", anchor="w").pack(fill="x")

            # Right Action Buttons
            btn_box = ctk.CTkFrame(main_box, fg_color="transparent")
            btn_box.pack(side="right", padx=(10, 0))

            ctk.CTkButton(
                btn_box,
                text="แก้ไข",
                width=65,
                height=32,
                fg_color="#E0F2FE",
                text_color="#0284C7",
                hover_color="#BAE6FD",
                corner_radius=6,
                font=("Helvetica", 11, "bold"),
                command=lambda i=item: self.open_edit_dialog(i)
            ).pack(side="left", padx=3)

            ctk.CTkButton(
                btn_box,
                text="ลบ",
                width=55,
                height=32,
                fg_color="#FEE2E2",
                text_color="#DC2626",
                hover_color="#FCA5A5",
                corner_radius=6,
                font=("Helvetica", 11, "bold"),
                command=lambda i=item: self.delete_medication(i)
            ).pack(side="left", padx=3)

    def filter_meds(self, event=None):
        q = self.search_entry.get().strip().lower()
        filtered = [m for m in self.medications if q in m["name"].lower() or q in m.get("properties", "").lower()]
        self.render_med_cards(filtered)

    def open_add_dialog(self):
        MedicationFormDialog(self, title="เพิ่มรายการยาใหม่", on_save_callback=self.save_medication)

    def open_edit_dialog(self, item):
        MedicationFormDialog(self, title="แก้ไขรายการยา", item=item, on_save_callback=self.save_medication)

    def save_medication(self, data, existing_item=None):
        if existing_item:
            existing_item.update(data)
        else:
            data["id"] = f"MED-{len(self.medications)+1:03d}"
            self.medications.append(data)

        self.filter_meds()

    def delete_medication(self, item):
        confirm = messagebox.askyesno("ยืนยันการลบ", f"คุณต้องการลบรายการยา '{item['name']}' ออกจากระบบหรือไม่?")
        if confirm:
            self.medications.remove(item)
            self.filter_meds()

if __name__ == "__main__":
    app = MainClinicApp()
    app.mainloop()