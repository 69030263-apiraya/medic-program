import json
import os
import tkinter as tk
from tkinter import messagebox, ttk


class SettingsWindow(tk.Toplevel):

  def __init__(self, parent):
    super().__init__(parent)
    self.title("⚙️ ตั้งค่าระบบ (Settings Module)")
    self.geometry("420x480")
    self.resizable(False, False)

    # ไฟล์สำหรับเก็บ Config Local
    self.config_file = "user_config.json"

    # ตัวแปรสำหรับเก็บค่า
    self.theme_var = tk.StringVar(value="Light")
    self.volume_var = tk.IntVar(value=80)
    self.line_token_var = tk.StringVar()

    # สร้าง UI Component
    self.create_widgets()

    # โหลดค่า Config เดิมที่บันทึกไว้
    self.load_config()

  def create_widgets(self):
    # Header
    header_frame = tk.Frame(self, pady=10)
    header_frame.pack(fill="x")
    title_label = tk.Label(
        header_frame,
        text="⚙️ ตั้งค่าระบบ",
        font=("Helvetica", 16, "bold"),
        fg="#2563EB",
    )
    title_label.pack()
    subtitle_label = tk.Label(
        header_frame,
        text="ปรับแต่งการทำงานและบันทึก Local Config",
        font=("Helvetica", 9),
        fg="gray",
    )
    subtitle_label.pack()

    # Content Frame
    content_frame = tk.Frame(self, padx=20, pady=10)
    content_frame.pack(fill="both", expand=True)

    # 1. เลือกธีมหน้าจอ (Theme)
    theme_frame = tk.LabelFrame(
        content_frame,
        text=" ธีมหน้าจอ ",
        font=("Helvetica", 10, "bold"),
        padx=10,
        pady=10,
    )
    theme_frame.pack(fill="x", pady=5)

    tk.Radiobutton(
        theme_frame,
        text="☀️ Light Mode",
        variable=self.theme_var,
        value="Light",
    ).pack(side="left", padx=10)
    tk.Radiobutton(
        theme_frame, text="🌙 Dark Mode", variable=self.theme_var, value="Dark"
    ).pack(side="left", padx=10)

    # 2. ปรับระดับเสียงเตือน (Volume)
    volume_frame = tk.LabelFrame(
        content_frame,
        text=" 🔔 ระดับเสียงเตือน ",
        font=("Helvetica", 10, "bold"),
        padx=10,
        pady=10,
    )
    volume_frame.pack(fill="x", pady=5)

    self.vol_label = tk.Label(
        volume_frame, text=f"ระดับเสียง: {self.volume_var.get()}%"
    )
    self.vol_label.pack(anchor="w")

    vol_scale = ttk.Scale(
        volume_frame,
        from_=0,
        to=100,
        variable=self.volume_var,
        command=self.update_volume_label,
    )
    vol_scale.pack(fill="x", pady=5)

    test_audio_btn = tk.Button(
        volume_frame,
        text="▶️ ทดลองฟังเสียง",
        command=self.test_sound,
        bg="#E5E7EB",
        font=("Helvetica", 9),
    )
    test_audio_btn.pack(anchor="e", pady=2)

    # 3. ช่องกรอก LINE Notify Token
    token_frame = tk.LabelFrame(
        content_frame,
        text=" 💬 LINE Notify Token ",
        font=("Helvetica", 10, "bold"),
        padx=10,
        pady=10,
    )
    token_frame.pack(fill="x", pady=5)

    token_entry = tk.Entry(
        token_frame,
        textvariable=self.line_token_var,
        font=("Helvetica", 10),
        show="*",
    )
    token_entry.pack(fill="x", pady=2)
    hint_label = tk.Label(
        token_frame,
        text="รับ Token ได้จากเว็บไซต์ LINE Notify",
        font=("Helvetica", 8),
        fg="gray",
    )
    hint_label.pack(anchor="w")

    # 4. ปุ่มบันทึกการตั้งค่า
    save_btn = tk.Button(
        self,
        text="💾 บันทึกการตั้งค่า (Save Config)",
        command=self.save_config,
        bg="#16A34A",
        fg="white",
        font=("Helvetica", 11, "bold"),
        pady=8,
    )
    save_btn.pack(fill="x", padx=20, pady=15)

  def update_volume_label(self, val):
    self.vol_label.config(text=f"ระดับเสียง: {int(float(val))}%")

  def test_sound(self):
    try:
      import winsound

      winsound.Beep(880, 250)
    except Exception:
      self.bell()

  def save_config(self):
    config_data = {
        "theme": self.theme_var.get(),
        "volume": self.volume_var.get(),
        "line_token": self.line_token_var.get(),
    }

    with open(self.config_file, "w", encoding="utf-8") as f:
      json.dump(config_data, f, ensure_ascii=False, indent=4)

    self.test_sound()
    messagebox.showinfo(
        "สำเร็จ", "💾 บันทึกการตั้งค่าลง Local Config เรียบร้อยแล้ว!"
    )

  def load_config(self):
    if os.path.exists(self.config_file):
      try:
        with open(self.config_file, "r", encoding="utf-8") as f:
          config_data = json.load(f)
          self.theme_var.set(config_data.get("theme", "Light"))
          self.volume_var.set(config_data.get("volume", 80))
          self.line_token_var.set(config_data.get("line_token", ""))
          self.update_volume_label(self.volume_var.get())
      except Exception as e:
        print("Error loading config:", e)


if __name__ == "__main__":
  root = tk.Tk()
  root.withdraw()
  app = SettingsWindow(root)
  app.protocol("WM_DELETE_WINDOW", root.destroy)
  app.mainloop()
  