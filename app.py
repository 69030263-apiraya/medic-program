import datetime
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk

# Import pymongo สำหรับจัดการ MongoDB (ถ้าต้องการเชื่อมต่อ DB จริง)
try:
    from pymongo import MongoClient

    # เปลี่ยน URL การเชื่อมต่อตามต้องการ
    client = MongoClient("mongodb://localhost:27017/")
    db = client["pharmacy_db"]
    medications_col = db["medications"]
    logs_col = db["logs"]
except Exception as e:
    print(f" Warning: ไม่สามารถเชื่อมต่อ MongoDB ได้ (ใช้งานโหมดจำลอง): {e}")
    medications_col = None
    logs_col = None

# จำลองฟังก์ชันตัดสต็อกของคนที่ 1
def delete_one_stock(med_name):
    print(f"[คนที่ 1 Integration] ตัดสต็อกยา: {med_name} เรียบร้อยแล้ว")

class MedicationSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ระบบตั้งตารางเวลาเตือนกินยา (Scheduler & Notification Module)")
        self.root.geometry("500x400")

        # รายการตารางเวลาเตือนกินยาในหน่วยความจำ
        self.schedules = []
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

        # เริ่มทำงาน Background Thread
        self.is_running = True
        self.checker_thread = threading.Thread(target=self.check_time_loop, daemon=True)
        self.checker_thread.start()

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
        self.med_combobox = ttk.Combobox(frame, values=["Paracetamol", "Aspirin", "Amoxicillin"], state="readonly")
        self.med_combobox.grid(row=0, column=1, sticky="ew", pady=5)
        if self.med_combobox['values']:
            self.med_combobox.current(0)

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
    
    
    
    
    def add_schedule(self):
        med_name = self.med_combobox.get()
        hh = self.hour_spin.get().zfill(2)
        mm = self.minute_spin.get().zfill(2)
        remind_time = f"{hh}:{mm}"

        schedule_item = {"med_name": med_name, "remind_time": remind_time, "date": datetime.date.today().strftime("%Y-%m-%d")}
        self.schedules.append(schedule_item)
        self.tree.insert("", "end", values=(med_name, remind_time))

        # insert_one() เพิ่มข้อมูลลง MongoDB (คลัง medications)
        if medications_col is not None:
            try:
                medications_col.insert_one(schedule_item)
            except Exception as e:
                print(f"MongoDB Error: {e}")

        messagebox.showinfo("สำเร็จ", f"ตั้งเวลาเตือน {med_name} ตอน {remind_time} น. เรียบร้อยแล้ว")

    def check_schedule_loop(self):
        """Background Thread เช็คเวลาปัจจุบันเทียบกับตารางทุกๆ 1 วินาที"""
        while self.is_running:
            now = datetime.datetime.now()
            current_time_str = now.strftime("%H:%M")
            current_second = now.second

            # ดึงข้อมูลตารางเวลาของวันปัจจุบัน (ใช้ find ใน MongoDB ถ้ามี)
            active_schedules = self.schedules
            if medications_col is not None:
                try:
                    today_str = datetime.date.today().strftime("%Y-%m-%d")
                    active_schedules = list(medications_col.find({"date": today_str}))
                except Exception as e:
                    pass

            # ตรวจสอบว่าตรงกับเวลาเตือนหรือไม่ (เช็คที่วินาที 00)
            if current_second == 0:
                for item in active_schedules:
                    trigger_key = f"{item['med_name']}_{item['remind_time']}_{datetime.date.today()}"
                    if item['remind_time'] == current_time_str and trigger_key not in self.triggered_times:
                        self.triggered_times.add(trigger_key)
                        # เรียก Pop-up Notification บน Main Thread
                        self.root.after(0, self.show_notification_popup, item['med_name'], item['remind_time'])

            time.sleep(1)

    def show_notification_popup(self, med_name, remind_time):
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
            
            # insert_one() บันทึกประวัติลง Collection logs
            log_data = {
                "med_name": med_name,
                "status": "Taken",
                "action_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            if logs_col is not None:
                try:
                    logs_col.insert_one(log_data)
                except Exception as e:
                    print(f"MongoDB Log Error: {e}")
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
                except Exception as e:
                    print(f"MongoDB Log Error: {e}")
            popup.destroy()

        # 3. ปุ่ม [เลื่อน 10 นาที (Snooze)]
        def on_snooze():
            snooze_time = (datetime.datetime.now() + datetime.timedelta(minutes=10)).strftime("%H:%M")
            snooze_item = {"med_name": med_name, "remind_time": snooze_time, "date": datetime.date.today().strftime("%Y-%m-%d")}
            self.schedules.append(snooze_item)
            
            messagebox.showinfo("Snooze", f"เลื่อนการเตือนยา {med_name} ไปอีก 10 นาที ({snooze_time} น.)")
            popup.destroy()

        ttk.Button(btn_frame, text="กินยาแล้ว", command=on_take).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="ข้าม", command=on_skip).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="เลื่อน 10 นาที", command=on_snooze).pack(side="left", padx=5)
    def check_time_loop(self):
        """ฟังก์ชันทำงานเบื้องหลังเพื่อคอยเช็คเวลาแจ้งเตือนทุกๆ 1 วินาที"""
        import time
        from datetime import datetime
        
        while self.is_running:
            now = datetime.now().strftime("%H:%M")
            # เช็ครายการเตือนที่ตั้งไว้
            for schedule in self.schedules:
                if schedule["time"] == now and now not in self.triggered_times:
                    self.triggered_times.add(now)
                    # แสดงป๊อบอัปแจ้งเตือนกินยา
                    self.show_notification_popup(schedule["med"], schedule["time"])
            time.sleep(1)

if __name__ == "__main__":
    root = tk.Tk()
    app = MedicationSchedulerApp(root)
    root.mainloop()
