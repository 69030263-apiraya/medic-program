import customtkinter as ctk

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# ข้อมูลจำลองคลังยา
MEDICATIONS_DATA = [
    {"id": "MED-001", "name": "Paracetamol 500mg", "category": "ยาลดไข้/แก้ปวด", "stock": 150, "unit": "กล่อง", "min_stock": 20},
    {"id": "MED-002", "name": "Amoxicillin 500mg", "category": "ยาฆ่าเชื้อ", "stock": 8, "unit": "กล่อง", "min_stock": 15},
    {"id": "MED-003", "name": "Ibuprofen 400mg", "category": "ยาแก้ปวด/แก้อักเสบ", "stock": 0, "unit": "กล่อง", "min_stock": 10},
    {"id": "MED-004", "name": "Cetirizine 10mg", "category": "ยาแก้แพ้", "stock": 85, "unit": "แผง", "min_stock": 20},
    {"id": "MED-005", "name": "Omeprazole 20mg", "category": "ยารักษาโรคกระเพาะ", "stock": 5, "unit": "กล่อง", "min_stock": 10},
    {"id": "MED-006", "name": "NSS Saline 0.9% 500ml", "category": "น้ำเกลือ/เวชภัณฑ์", "stock": 42, "unit": "ขวด", "min_stock": 15},
]

class MedicationInventoryApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ระบบจัดการคลังยา - Medication Inventory")
        self.geometry("900x650")
        self.resizable(False, False)
        self.configure(fg_color="#F1F5F9")

        self.medications = MEDICATIONS_DATA.copy()

        # ---------------- 1. Top Header Banner ----------------
        self.header_frame = ctk.CTkFrame(self, fg_color="#0D9488", corner_radius=0, height=90)  # สี Teal สดใส
        self.header_frame.pack(fill="x", side="top")
        self.header_frame.pack_propagate(False)

        self.header_title = ctk.CTkLabel(
            self.header_frame,
            text="💊 ระบบจัดการคลังยา (Medication Inventory)",
            font=("Helvetica", 20, "bold"),
            text_color="#FFFFFF"
        )
        self.header_title.pack(anchor="w", padx=24, pady=(18, 2))

        self.header_subtitle = ctk.CTkLabel(
            self.header_frame,
            text="รายการยาคงคลัง ตรวจสอบสถานะสต็อก และปรับปรุงจำนวนยา",
            font=("Helvetica", 12),
            text_color="#CCFBF1"
        )
        self.header_subtitle.pack(anchor="w", padx=24)

        # ---------------- 2. Control & Search Bar ----------------
        self.control_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.control_frame.pack(fill="x", padx=20, pady=(16, 10))

        # ช่องค้นหา
        self.search_entry = ctk.CTkEntry(
            self.control_frame,
            placeholder_text="🔍 ค้นหาชื่อยา หรือรหัสยา...",
            width=280,
            height=38,
            corner_radius=10,
            border_color="#CBD5E1",
            fg_color="#FFFFFF"
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.filter_medications)

        # ตัวกรองหมวดหมู่
        categories = ["ทุกหมวดหมู่", "ยาลดไข้/แก้ปวด", "ยาฆ่าเชื้อ", "ยาแก้ปวด/แก้อักเสบ", "ยาแก้แพ้", "ยารักษาโรคกระเพาะ", "น้ำเกลือ/เวชภัณฑ์"]
        self.category_option = ctk.CTkOptionMenu(
            self.control_frame,
            values=categories,
            width=180,
            height=38,
            corner_radius=10,
            fg_color="#0D9488",
            button_color="#09756B",
            button_hover_color="#045952",
            command=lambda _: self.filter_medications()
        )
        self.category_option.pack(side="left")

        # ปุ่มเพิ่มรายการยา
        self.add_btn = ctk.CTkButton(
            self.control_frame,
            text="+ เพิ่มรายการยา",
            fg_color="#10B981",
            hover_color="#059669",
            height=38,
            corner_radius=10,
            font=("Helvetica", 12, "bold"),
            command=self.add_medication_dialog
        )
        self.add_btn.pack(side="right")

        # ---------------- 3. Table Header Labels ----------------
        self.table_header = ctk.CTkFrame(self, fg_color="#E2E8F0", height=36, corner_radius=8)
        self.table_header.pack(fill="x", padx=20, pady=(5, 5))

        headers = [("รหัส/ชื่อยา", 250), ("หมวดหมู่", 170), ("คงเหลือ", 130), ("สถานะ", 110), ("การจัดการ", 100)]
        for text, width in headers:
            lbl = ctk.CTkLabel(
                self.table_header, 
                text=text, 
                font=("Helvetica", 12, "bold"), 
                text_color="#475569", 
                width=width, 
                anchor="w"
            )
            lbl.pack(side="left", padx=10)

        # ---------------- 4. Scrollable Container for Cards ----------------
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        self.render_medications(self.medications)

    def render_medications(self, items):
        # ล้างการ์ดเดิมออกก่อนวาดใหม่
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not items:
            empty_lbl = ctk.CTkLabel(
                self.scrollable_frame,
                text="ไม่พบรายการยาที่ตรงกับการค้นหา",
                font=("Helvetica", 14),
                text_color="#94A3B8"
            )
            empty_lbl.pack(pady=40)
            return

        for item in items:
            self.create_med_card(item)

    def create_med_card(self, item):
        # กำหนดสี Badge ตามสถานะสต็อก
        if item["stock"] <= 0:
            status_text = "หมดสต็อก"
            bg_status, fg_status = "#FEE2E2", "#B91C1C"
        elif item["stock"] <= item["min_stock"]:
            status_text = "สต็อกต่ำ"
            bg_status, fg_status = "#FEF3C7", "#B45309"
        else:
            status_text = "พร้อมจ่าย"
            bg_status, fg_status = "#DCFCE7", "#15803D"

        card = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color="#FFFFFF",
            corner_radius=12,
            height=65,
            border_width=1,
            border_color="#E2E8F0"
        )
        card.pack(fill="x", pady=4)

        # 1. ชื่อและรหัสยา
        name_frame = ctk.CTkFrame(card, fg_color="transparent", width=250)
        name_frame.pack(side="left", padx=10)
        
        ctk.CTkLabel(name_frame, text=item["name"], font=("Helvetica", 13, "bold"), text_color="#0F172A", anchor="w").pack(anchor="w")
        ctk.CTkLabel(name_frame, text=f"รหัส: {item['id']}", font=("Helvetica", 10), text_color="#64748B", anchor="w").pack(anchor="w")

        # 2. หมวดหมู่
        ctk.CTkLabel(card, text=item["category"], font=("Helvetica", 12), text_color="#334155", width=170, anchor="w").pack(side="left", padx=10)

        # 3. จำนวนคงเหลือ
        ctk.CTkLabel(card, text=f"{item['stock']} {item['unit']}", font=("Helvetica", 13, "bold"), text_color="#0F172A", width=130, anchor="w").pack(side="left", padx=10)

        # 4. Badge แสดงสถานะ
        badge_frame = ctk.CTkFrame(card, fg_color=bg_status, corner_radius=12, width=90, height=26)
        badge_frame.pack(side="left", padx=10)
        badge_frame.pack_propagate(False)
        ctk.CTkLabel(badge_frame, text=status_text, font=("Helvetica", 11, "bold"), text_color=fg_status).pack(expand=True)

        # 5. ปุ่มจัดการ (แก้ไขสต็อก)
        action_frame = ctk.CTkFrame(card, fg_color="transparent", width=100)
        action_frame.pack(side="left", padx=10)

        edit_btn = ctk.CTkButton(
            action_frame,
            text="ปรับสต็อก",
            width=70,
            height=28,
            fg_color="#3B82F6",
            hover_color="#1D4ED8",
            corner_radius=6,
            font=("Helvetica", 11),
            command=lambda i=item: self.edit_stock_dialog(i)
        )
        edit_btn.pack(side="left")

    def filter_medications(self, event=None):
        query = self.search_entry.get().strip().lower()
        selected_cat = self.category_option.get()

        filtered = []
        for med in self.medications:
            match_query = query in med["name"].lower() or query in med["id"].lower()
            match_cat = (selected_cat == "ทุกหมวดหมู่") or (med["category"] == selected_cat)
            
            if match_query and match_cat:
                filtered.append(med)

        self.render_medications(filtered)

    def add_medication_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("เพิ่มรายการยาใหม่")
        dialog.geometry("360x380")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="เพิ่มรายการยาคงคลัง", font=("Helvetica", 16, "bold")).pack(pady=15)

        entry_name = ctk.CTkEntry(dialog, placeholder_text="ชื่อยา (เช่น Paracetamol 500mg)", width=280)
        entry_name.pack(pady=8)

        entry_cat = ctk.CTkEntry(dialog, placeholder_text="หมวดหมู่ยา", width=280)
        entry_cat.pack(pady=8)

        entry_stock = ctk.CTkEntry(dialog, placeholder_text="จำนวนสต็อกเริ่มต้น", width=280)
        entry_stock.pack(pady=8)

        entry_unit = ctk.CTkEntry(dialog, placeholder_text="หน่วยนับ (เช่น กล่อง, แผง, ขวด)", width=280)
        entry_unit.pack(pady=8)

        def save_new():
            name = entry_name.get().strip()
            cat = entry_cat.get().strip()
            stock = entry_stock.get().strip()
            unit = entry_unit.get().strip()

            if name and cat and stock.isdigit():
                new_id = f"MED-{len(self.medications)+1:03d}"
                self.medications.append({
                    "id": new_id,
                    "name": name,
                    "category": cat,
                    "stock": int(stock),
                    "unit": unit if unit else "หน่วย",
                    "min_stock": 10
                })
                self.filter_medications()
                dialog.destroy()

        ctk.CTkButton(dialog, text="บันทึกรายการ", fg_color="#10B981", hover_color="#059669", width=280, command=save_new).pack(pady=20)

    def edit_stock_dialog(self, item):
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"ปรับสต็อก - {item['name']}")
        dialog.geometry("320x200")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=f"ปรับจำนวนสต็อก\n{item['name']}", font=("Helvetica", 14, "bold")).pack(pady=15)

        stock_entry = ctk.CTkEntry(dialog, width=200)
        stock_entry.insert(0, str(item["stock"]))
        stock_entry.pack(pady=10)

        def update():
            val = stock_entry.get().strip()
            if val.isdigit():
                item["stock"] = int(val)
                self.filter_medications()
                dialog.destroy()

        ctk.CTkButton(dialog, text="อัปเดตสต็อก", fg_color="#2563EB", width=200, command=update).pack(pady=10)

if __name__ == "__main__":
    app = MedicationInventoryApp()
    app.mainloop()