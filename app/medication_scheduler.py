import datetime
import json
import os
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk

from pymongo import MongoClient
from pymongo.errors import PyMongoError

client = MongoClient("mongodb://localhost:27017/")
logs_col = client["pharmacy_db"]["logs"]

# จำลองฟังก์ชันตัดสต็อกของคนที่ 1
def delete_one_stock(med_name):
    print(f"[คนที่ 1 Integration] ตัดสต็อกยา: {med_name} เรียบร้อยแล้ว")


def _get_schedule_storage_path():
    local_app_data = os.environ.get("LOCALAPPDATA")
    if not local_app_data:
        local_app_data = os.path.join(
            os.path.expanduser("~"), "AppData", "Local"
        )
    return os.path.join(
        local_app_data, "MedicProgram", "medication_schedules.json"
    )


class MedicationSchedulerApp:
    def __init__(self, root, user_id="local", medicines=None):
        self.root = root
        self.user_id = user_id
        self.root.title("ระบบตั้งตารางเวลาเตือนกินยา (Scheduler & Notification Module)")
        self.root.geometry("500x400")

        self.storage_path = _get_schedule_storage_path()
        self.schedules = self._load_schedules()
        self.medicines_by_label = {}
        self.medicines = medicines or []
        self.triggered_times = set()

        # --- 1. ตั้งค่าสไตล์สีสันทั้งหมดไว้ตรงนี้ ---
        bg_color = "#EBF2F7"        # สีฟ้าพาสเทลพื้นหลัง
        card_color = "#FFFFFF"      # สีขาวสำหรับกรอบเนื้อหา
        primary_color = "#2B7A78"   # สีเขียวอมฟ้าเข้ม
        primary_hover = "#17252A"

        self.root.configure(bg=bg_color)

        style = ttk.Style()
        style.theme_use("clam")

        # บังคับเปลี่ยนสี Frame และ LabelFrame ทั้งหมด
        style.configure("TFrame", background=bg_color)
        style.configure("TLabelframe", background=card_color, relief="flat", borderwidth=1)
        style.configure("TLabelframe.Label", background=card_color, foreground=primary_color, font=("Segoe UI", 11, "bold"))

        # ตัวหนังสือ (Label)
        style.configure("TLabel", background=card_color, foreground="#222222", font=("Segoe UI", 10))

        # ปุ่มกด (Button)
        style.configure("TButton", background=primary_color, foreground="white", font=("Segoe UI", 10, "bold"), padding=(10, 5), relief="flat")
        style.map("TButton", background=[("active", primary_hover)], foreground=[("active", "white")])

        # ตาราง (Treeview)
        style.configure("Treeview", background="white", fieldbackground="white", rowheight=26, font=("Segoe UI", 10), borderwidth=0)
        style.configure("Treeview.Heading", background=primary_color, foreground="white", font=("Segoe UI", 10, "bold"), relief="flat")
        style.map("Treeview.Heading", background=[("active", primary_hover)])

        # --- 2. เรียกสร้าง UI ---
        self.setup_ui()
        self.update_medicines(self.medicines)

        # เริ่มทำงาน Background Thread
        self.is_running = True
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.checker_thread = threading.Thread(target=self.check_time_loop, daemon=True)
        self.checker_thread.start()

    def close(self):
        self.is_running = False
        self.root.destroy()

    def setup_ui(self):
        """หน้าตั้งตารางเวลา (Schedule Setup)"""
        # สร้าง Frame หลักครอบเพื่อคุมสีพื้นหลัง
        main_container = ttk.Frame(self.root)
        main_container.pack(fill="both", expand=True)

        frame = ttk.LabelFrame(main_container, text="ตั้งตารางเวลาเตือนกินยา", padding=15)
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(3, weight=1)

        # 1. เลือกยาจากคลัง
        ttk.Label(frame, text="เลือกยาจากคลัง:").grid(row=0, column=0, sticky="w", pady=5)
        self.med_combobox = ttk.Combobox(frame, values=[], state="readonly")
        self.med_combobox.grid(row=0, column=1, sticky="ew", pady=5)

        # 2. กำหนดเวลาเตือน
        ttk.Label(frame, text="กำหนดเวลาเตือน (HH:MM):").grid(row=1, column=0, sticky="w", pady=5)
        time_frame = ttk.Frame(frame)
        time_frame.grid(row=1, column=1, sticky="w", pady=5)

        self.hour_spin = ttk.Spinbox(time_frame, from_=0, to=23, width=5, format="%02.0f")
        self.hour_spin.set("08")
        self.hour_spin.pack(side="left")

        # เปลี่ยนสไตล์ Label ตัวคั่นเวลาให้พื้นหลังกลมกลืน
        colon_label = tk.Label(time_frame, text=" : ", bg="white", font=("Segoe UI", 10, "bold"))
        colon_label.pack(side="left")

        self.minute_spin = ttk.Spinbox(time_frame, from_=0, to=59, width=5, format="%02.0f")
        self.minute_spin.set("00")
        self.minute_spin.pack(side="left")

        # ปุ่มเพิ่มตารางเวลา
        add_btn = ttk.Button(frame, text="เพิ่มตารางเวลาเตือน", command=self.add_schedule)
        add_btn.grid(row=2, column=0, columnspan=2, pady=12)

        # 3. ตารางแสดงรายการเตือนที่ตั้งไว้
        self.tree = ttk.Treeview(frame, columns=("med", "time"), show="headings")
        self.tree.heading("med", text="ชื่อยา")
        self.tree.heading("time", text="เวลาเตือน")
        self.tree.column("med", stretch=True)
        self.tree.column("time", stretch=True)
        
        self.tree.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=5)

        for item in self.schedules:
            self.tree.insert(
                "", "end", values=(item["med_name"], item["remind_time"])
            )

    def update_medicines(self, medicines):
        self.medicines = medicines
        selected_id = None
        selected = self.medicines_by_label.get(self.med_combobox.get())
        if selected:
            selected_id = selected.get("medId")

        self.medicines_by_label = {}
        for medicine in medicines:
            med_id = medicine.get("medId")
            med_name = medicine.get("medName")
            if not isinstance(med_id, str) or not isinstance(med_name, str):
                continue
            label = med_name
            if label in self.medicines_by_label:
                label = f"{med_name} · {med_id[:8]}"
            self.medicines_by_label[label] = medicine

        labels = list(self.medicines_by_label)
        self.med_combobox.configure(values=labels)
        self.med_combobox.configure(state="readonly" if labels else "disabled")
        selected_label = next(
            (
                label
                for label, medicine in self.medicines_by_label.items()
                if medicine.get("medId") == selected_id
            ),
            labels[0] if labels else "",
        )
        self.med_combobox.set(selected_label)

    def _load_schedules(self):
        if not os.path.exists(self.storage_path):
            return []
        try:
            with open(self.storage_path, "r", encoding="utf-8") as schedule_file:
                saved_schedules = json.load(schedule_file)
        except (OSError, ValueError, TypeError) as error:
            messagebox.showerror(
                "โหลดตารางเตือนไม่สำเร็จ",
                f"ไม่สามารถอ่านตารางเตือนจากเครื่องได้: {error}",
                parent=self.root,
            )
            return []
        if not isinstance(saved_schedules, dict):
            messagebox.showerror(
                "โหลดตารางเตือนไม่สำเร็จ",
                "รูปแบบข้อมูลตารางเตือนในเครื่องไม่ถูกต้อง",
                parent=self.root,
            )
            return []
        schedules = saved_schedules.get(self.user_id, [])
        if not isinstance(schedules, list) or any(
            not isinstance(item, dict)
            or not isinstance(item.get("med_name"), str)
            or not isinstance(item.get("remind_time"), str)
            for item in schedules
        ):
            messagebox.showerror(
                "โหลดตารางเตือนไม่สำเร็จ",
                "รูปแบบข้อมูลตารางเตือนของผู้ใช้นี้ไม่ถูกต้อง",
                parent=self.root,
            )
            return []
        return schedules

    def _save_schedules(self, schedules):
        saved_schedules = {}
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as schedule_file:
                    saved_schedules = json.load(schedule_file)
            except (OSError, ValueError, TypeError) as error:
                messagebox.showerror(
                    "บันทึกตารางเตือนไม่สำเร็จ",
                    f"ไม่สามารถอ่านข้อมูลเดิมในเครื่องได้: {error}",
                    parent=self.root,
                )
                return False
            if not isinstance(saved_schedules, dict):
                messagebox.showerror(
                    "บันทึกตารางเตือนไม่สำเร็จ",
                    "รูปแบบข้อมูลตารางเตือนในเครื่องไม่ถูกต้อง",
                    parent=self.root,
                )
                return False

        saved_schedules[self.user_id] = schedules
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, "w", encoding="utf-8") as schedule_file:
                json.dump(
                    saved_schedules,
                    schedule_file,
                    ensure_ascii=False,
                    indent=2,
                )
        except (OSError, TypeError, ValueError) as error:
            messagebox.showerror(
                "บันทึกตารางเตือนไม่สำเร็จ",
                f"ไม่สามารถบันทึกตารางเตือนลงเครื่องได้: {error}",
                parent=self.root,
            )
            return False
        return True

    def add_schedule(self):
        medicine = self.medicines_by_label.get(self.med_combobox.get())
        if medicine is None:
            messagebox.showerror(
                "เพิ่มตารางเวลาเตือน",
                "กรุณาเลือกยาจากรายการยาปัจจุบันของคุณ",
                parent=self.root,
            )
            return
        med_name = medicine["medName"]
        hh = self.hour_spin.get().zfill(2)
        mm = self.minute_spin.get().zfill(2)
        remind_time = f"{hh}:{mm}"

        schedule_item = {
            "med_id": medicine["medId"],
            "med_name": med_name,
            "remind_time": remind_time,
        }
        updated_schedules = self.schedules + [schedule_item]
        if not self._save_schedules(updated_schedules):
            return
        self.schedules = updated_schedules
        self.tree.insert("", "end", values=(med_name, remind_time))

        messagebox.showinfo("สำเร็จ", f"ตั้งเวลาเตือน {med_name} ตอน {remind_time} น. เรียบร้อยแล้ว")

    def check_time_loop(self):
        """Background Thread เช็คเวลาปัจจุบันเทียบกับตารางทุกๆ 1 วินาที"""
        while self.is_running:
            now = datetime.datetime.now()
            current_time_str = now.strftime("%H:%M")
            current_second = now.second

            active_schedules = self.schedules

            # ตรวจสอบว่าตรงกับเวลาเตือนหรือไม่ (เช็คที่วินาที 00)
            if current_second == 0:
                for item in active_schedules:
                    trigger_key = f"{item['med_name']}_{item['remind_time']}_{datetime.date.today()}"
                    if item['remind_time'] == current_time_str and trigger_key not in self.triggered_times:
                        self.triggered_times.add(trigger_key)
                        # เรียก Pop-up Notification บน Main Thread
                        self.root.after(
                            0,
                            self.show_notification_popup,
                            item.get("med_id"),
                            item["med_name"],
                            item["remind_time"],
                        )

            time.sleep(1)

    def show_notification_popup(self, med_id, med_name, remind_time):
        """หน้าต่างแจ้งเตือน (Pop-up Notification Window) เด้งขึ้นมากลางจอ"""
        popup = tk.Toplevel(self.root)
        popup.title(" แจ้งเตือนกินยา!")
        popup.geometry("350x200")

        # ให้ Pop-up อยู่ตรงกลางจอภาพและอยู่ด้านบนสุด (Always on Top)
        popup.attributes("-topmost", True)
        popup.grab_set()

        # เสียงเตือน (Beep)
        self.root.bell()

        ttk.Label(popup, text="ถึงเวลาทานยาแล้ว!", font=("Helvetica", 14, "bold"), foreground="red").pack(pady=10)
        ttk.Label(popup, text=f"ยา: {med_name}\nเวลา: {remind_time} น.", font=("Helvetica", 11), justify="center").pack(pady=5)

        btn_frame = ttk.Frame(popup)
        btn_frame.pack(pady=15)

        # 1. ปุ่ม [กินยาแล้ว]
        def on_take():
            # สั่งเรียกฟังก์ชันตัดสต็อกของคนแรก
            delete_one_stock(med_name)
            
            log_data = {
                "med_name": med_name,
                "status": "Taken",
                "action_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            if logs_col is not None:
                try:
                    logs_col.insert_one(log_data)
                except PyMongoError as error:
                    print(f"MongoDB Log Error: {error}")
            print(f"[Log Created]: {log_data}")

            popup.destroy()

        # 2. ปุ่ม [ข้าม]
        def on_skip():
            log_data = {
                "med_name": med_name,
                "status": "Skipped",
                "action_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            if logs_col is not None:
                try:
                    logs_col.insert_one(log_data)
                except PyMongoError as error:
                    print(f"MongoDB Log Error: {error}")
            print(f"[Log Created]: {log_data}")
            popup.destroy()

        # 3. ปุ่ม [เลื่อน 10 นาที (Snooze)]
        def on_snooze():
            snooze_time = (datetime.datetime.now() + datetime.timedelta(minutes=10)).strftime("%H:%M")
            snooze_item = {
                "med_id": med_id,
                "med_name": med_name,
                "remind_time": snooze_time,
            }
            updated_schedules = self.schedules + [snooze_item]
            if not self._save_schedules(updated_schedules):
                return
            self.schedules = updated_schedules
            
            messagebox.showinfo("Snooze", f"เลื่อนการเตือนยา {med_name} ไปอีก 10 นาที ({snooze_time} น.)")
            popup.destroy()

        ttk.Button(btn_frame, text="กินยาแล้ว", command=on_take).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="ข้าม", command=on_skip).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="เลื่อน 10 นาที", command=on_snooze).pack(side="left", padx=5)
if __name__ == "__main__":
    root = tk.Tk()
    app = MedicationSchedulerApp(root)
    root.mainloop()
