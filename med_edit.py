import customtkinter as ctk
from tkinter import messagebox

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# ---------------- ข้อมูลจำลองคลังยา (อัปเดตฟิลด์ใหม่) ----------------
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
        "properties": "ยาลดการหลั่งกรดในกระเพาะอาหาร รักษาแผลในกระเพาะ",
        "stock": 5,
        "unit": "เม็ด",
        "timing": "ก่อนอาหาร (30 นาที)",
        "exp_date": "2026-08-20",
        "min_stock": 10
    }
]

# ==================== MODAL DIALOG: ฟอร์ม เพิ่ม/แก้ไข รายการยา ====================
class MedicationFormDialog(ctk.CTkToplevel):
    def __init__(self, parent, title="รายการยา", item=None, on_save_callback=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("460x620")
        self.resizable(False, False)
        self.grab_set()  # ล็อกโฟกัสไว้ที่ Modal

        self.item = item
        self.on_save_callback = on_save_callback

        # --- Header ---
        header_color = "#0284C7" if item else "#10B981"  # สีฟ้าถ้าแก้ไข / สีเขียวถ้าเพิ่มใหม่
        header = ctk.CTkFrame(self, fg_color=header_color, height=60, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        header_txt = "✏️ แก้ไขข้อมูลยา" if item else "➕ เพิ่มรายการยาใหม่"
        ctk.CTkLabel(header, text=header_txt, font=("Helvetica", 16, "bold"), text_color="#FFFFFF").pack(pady=16)

        # --- Form Body ---
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=24, pady=16)

        # 1. ชื่อยา
        ctk.CTkLabel(body, text="ชื่อยา / ขนาดความแรง *", font=("Helvetica", 12, "bold"), text_color="#0F172A").pack(anchor="w", pady=(0, 2))
        self.entry_name = ctk.CTkEntry(body, placeholder_text="เช่น Paracetamol 500mg", height=38, corner_radius=8)
        self.entry_name.pack(fill="x", pady=(0, 10))

        # 2. สรรพคุณ
        ctk.CTkLabel(body, text="สรรพคุณ / ข้อบ่งใช้", font=("Helvetica", 12, "bold"), text_color="#0F172A").pack(anchor="w", pady=(0, 2))
        self.txt_properties = ctk.CTkTextbox(body, height=65, corner_radius=8, fg_color="#F8FAFC", border_color="#CBD5E1", border_width=1)
        self.txt_properties.pack(fill="x", pady=(0, 10))

        # 3. จำนวนคงเหลือ & หน่วยนับ (Row 2 Columns)
        stock_frame = ctk.CTkFrame(body, fg_color="transparent")
        stock_frame.pack(fill="x", pady=(0, 10))

        # จำนวนคงเหลือ
        col1 = ctk.CTkFrame(stock_frame, fg_color="transparent")
        col1.pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkLabel(col1, text="จำนวนคงเหลือ *", font=("Helvetica", 12, "bold"), text_color="#0F172A").pack(anchor="w", pady=(0, 2))
        self.entry_stock = ctk.CTkEntry(col1, placeholder_text="เช่น 100", height=38, corner_radius=8)
        self.entry_stock.pack(fill="x")

        # หน่วยนับ
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

        # --- Footer Buttons ---
        btn_box = ctk.CTkFrame(body, fg_color="transparent")
        btn_box.pack(fill="x")

        ctk.CTkButton(btn_box, text="ยกเลิก", fg_color="#F1F5F9", text_color="#475569", hover_color="#E2E8F0", height=40, corner_radius=8, command=self.destroy).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkButton(btn_box, text="บันทึกข้อมูล", fg_color=header_color, hover_color="#059669", height=40, corner_radius=8, font=("Helvetica", 12, "bold"), command=self.save).pack(side="right", expand=True, fill="x", padx=(6, 0))

        # ใส่ข้อมูลเดิมเข้าไปหากเป็นการแก้ไข (Edit Mode)
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

        # Validation
        if not name or not stock:
            messagebox.showwarning("ข้อผิดพลาด", "กรุณากรอกชื่อยาและจำนวนคงเหลือ")
            return

        if not stock.isdigit():
            messagebox.showwarning("ข้อผิดพลาด", "จำนวนคงเหลือต้องเป็นตัวเลขเท่านั้น")
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

# ==================== MAIN PAGE: หน้าคลังยาพร้อมระบบ CRUD ====================
class MedicationManagementApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ระบบจัดการข้อมูลยา - Medication Management")
        self.geometry("950x650")
        self.configure(fg_color="#F8FAFC")

        self.medications = MEDICATIONS_DATA.copy()

        # --- Top Banner ---
        header = ctk.CTkFrame(self, fg_color="#0D9488", corner_radius=0, height=85)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="💊 คลังยาและเวชภัณฑ์ (Medication Directory)", font=("Helvetica", 18, "bold"), text_color="#FFFFFF").pack(anchor="w", padx=24, pady=(18, 2))
        ctk.CTkLabel(header, text="เพิ่ม แก้ไข ลบ และติดตามสถานะวันหมดอายุและวิธีทานยา", font=("Helvetica", 12), text_color="#CCFBF1").pack(anchor="w", padx=24)

        # --- Control Bar ---
        ctrl = ctk.CTkFrame(self, fg_color="transparent")
        ctrl.pack(fill="x", padx=20, pady=16)

        self.search_entry = ctk.CTkEntry(ctrl, placeholder_text="🔍 ค้นหาชื่อยา, สรรพคุณ...", width=320, height=38, corner_radius=8)
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

        # --- Scrollable Container ---
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.render_med_cards(self.medications)

    def render_med_cards(self, items):
        for w in self.scroll_frame.winfo_children():
            w.destroy()

        if not items:
            ctk.CTkLabel(self.scroll_frame, text="ไม่พบรายการยาที่ตรงกับการค้นหา", font=("Helvetica", 13), text_color="#94A3B8").pack(pady=40)
            return

        for item in items:
            card = ctk.CTkFrame(self.scroll_frame, fg_color="#FFFFFF", corner_radius=12, border_width=1, border_color="#E2E8F0")
            card.pack(fill="x", pady=6, padx=2)

            main_box = ctk.CTkFrame(card, fg_color="transparent")
            main_box.pack(fill="x", padx=16, pady=12)

            # Left Section: รายละเอียดหลัก
            left_info = ctk.CTkFrame(main_box, fg_color="transparent")
            left_info.pack(side="left", expand=True, fill="x")

            # ชื่อยา & EXP
            top_line = ctk.CTkFrame(left_info, fg_color="transparent")
            top_line.pack(fill="x", anchor="w")

            ctk.CTkLabel(top_line, text=item["name"], font=("Helvetica", 14, "bold"), text_color="#0F172A").pack(side="left")
            
            # Badge วันหมดอายุ
            exp_badge = ctk.CTkFrame(top_line, fg_color="#FEF3C7", corner_radius=6)
            exp_badge.pack(side="left", padx=10)
            ctk.CTkLabel(exp_badge, text=f"EXP: {item.get('exp_date', 'N/A')}", font=("Helvetica", 10, "bold"), text_color="#D97706").pack(padx=6, pady=2)

            # สรรพคุณ
            ctk.CTkLabel(left_info, text=f"สรรพคุณ: {item.get('properties', '-')}", font=("Helvetica", 11), text_color="#64748B", anchor="w").pack(fill="x", pady=(2, 4))

            # วิธีทาน & สต็อก
            details = f"🍽️ วิธีทาน: {item.get('timing', '-')}   |   📦 สต็อก: {item['stock']} {item.get('unit', 'หน่วย')}"
            ctk.CTkLabel(left_info, text=details, font=("Helvetica", 11, "bold"), text_color="#0369A1", anchor="w").pack(fill="x")

            # Right Section: ปุ่มจัดการ (Edit / Delete)
            btn_box = ctk.CTkFrame(main_box, fg_color="transparent")
            btn_box.pack(side="right", padx=(10, 0))

            # ปุ่มแก้ไข
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

            # ปุ่มลบ
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
            # แก้ไขข้อมูลเดิม
            existing_item.update(data)
        else:
            # เพิ่มข้อมูลใหม่
            data["id"] = f"MED-{len(self.medications)+1:03d}"
            self.medications.append(data)

        self.filter_meds()

    def delete_medication(self, item):
        confirm = messagebox.askyesno("ยืนยันการลบ", f"คุณต้องการลบรายการยา '{item['name']}' ออกจากระบบหรือไม่?")
        if confirm:
            self.medications.remove(item)
            self.filter_meds()

if __name__ == "__main__":
    app = MedicationManagementApp()
    app.mainloop()
