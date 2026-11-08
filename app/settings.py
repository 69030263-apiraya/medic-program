import json
import os
import tkinter as tk
from tkinter import messagebox


class ModernSettingsWindow:
	def __init__(self, root=None):
		if root is None:
			self.root = tk.Tk()
			self.is_standalone = True
		else:
			self.root = tk.Toplevel(root)
			self.is_standalone = False

		self.root.title("การตั้งค่าระบบ - Settings")
		self.root.geometry("520x680")
		self.root.resizable(False, False)

		self.config_path = "user_config.json"
		self.themes = {
			"light": {
				"bg": "#F8FAFC",
				"card": "#FFFFFF",
				"text": "#0F172A",
				"subtext": "#64748B",
				"border": "#E2E8F0",
				"primary": "#2563EB",
				"primary_hover": "#1D4ED8",
				"input_bg": "#F1F5F9",
				"entry_border": "#CBD5E1",
			},
			"dark": {
				"bg": "#0F172A",
				"card": "#1E293B",
				"text": "#F8FAFC",
				"subtext": "#94A3B8",
				"border": "#334155",
				"primary": "#3B82F6",
				"primary_hover": "#60A5FA",
				"input_bg": "#0F172A",
				"entry_border": "#475569",
			},
		}

		self.current_theme = tk.StringVar(value="light")
		self.volume_level = tk.IntVar(value=70)
		self.line_token = tk.StringVar(value="")
		self.notify_enabled = tk.BooleanVar(value=True)

		self.load_config()
		self.setup_ui()
		self.apply_theme(self.current_theme.get())

		if self.is_standalone:
			self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)

	def load_config(self):
		"""โหลดค่าคอนฟิกจากไฟล์ JSON"""
		if os.path.exists(self.config_path):
			try:
				with open(self.config_path, "r", encoding="utf-8") as config_file:
					data = json.load(config_file)
				theme = data.get("theme", "light")
				self.current_theme.set(theme if theme in self.themes else "light")
				self.volume_level.set(max(0, min(100, int(data.get("volume", 70)))))
				self.line_token.set(str(data.get("line_token", "")))
				self.notify_enabled.set(bool(data.get("notify_enabled", True)))
			except (OSError, ValueError, TypeError, json.JSONDecodeError) as error:
				print(f"Error loading config: {error}")

	def save_config(self):
		"""บันทึกค่าคอนฟิกลงไฟล์ JSON"""
		data = {
			"theme": self.current_theme.get(),
			"volume": self.volume_level.get(),
			"line_token": self.line_token.get().strip(),
			"notify_enabled": self.notify_enabled.get(),
		}
		try:
			with open(self.config_path, "w", encoding="utf-8") as config_file:
				json.dump(data, config_file, ensure_ascii=False, indent=4)
			messagebox.showinfo(
				"สำเร็จ", "บันทึกการตั้งค่าเรียบร้อยแล้ว!", parent=self.root
			)
		except (OSError, TypeError, ValueError) as error:
			messagebox.showerror(
				"ผิดพลาด", f"ไม่สามารถบันทึกข้อมูลได้: {error}", parent=self.root
			)

	def setup_ui(self):
		"""สร้างโครงสร้างหน้าต่าง (Card-based UI Layout)"""
		self.main_frame = tk.Frame(self.root)
		self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

		self.header_label = tk.Label(
			self.main_frame,
			text="⚙️ ตั้งค่าการใช้งาน",
			font=("Segoe UI", 18, "bold"),
			anchor="w",
		)
		self.header_label.pack(fill="x", pady=(0, 15))

		self.card_theme = tk.LabelFrame(
			self.main_frame,
			text=" 🎨 ธีมและการแสดงผล ",
			font=("Segoe UI", 11, "bold"),
			padx=15,
			pady=15,
			bd=1,
			relief="solid",
		)
		self.card_theme.pack(fill="x", pady=(0, 15))

		self.radio_light = tk.Radiobutton(
			self.card_theme,
			text="☀️ โหมดสว่าง (Light Mode)",
			variable=self.current_theme,
			value="light",
			font=("Segoe UI", 10),
			command=self.on_theme_change,
		)
		self.radio_light.pack(anchor="w", pady=4)

		self.radio_dark = tk.Radiobutton(
			self.card_theme,
			text="🌙 โหมดมืด (Dark Mode)",
			variable=self.current_theme,
			value="dark",
			font=("Segoe UI", 10),
			command=self.on_theme_change,
		)
		self.radio_dark.pack(anchor="w", pady=4)

		self.card_sound = tk.LabelFrame(
			self.main_frame,
			text=" 🔊 การแจ้งเตือนด้วยเสียง ",
			font=("Segoe UI", 11, "bold"),
			padx=15,
			pady=15,
			bd=1,
			relief="solid",
		)
		self.card_sound.pack(fill="x", pady=(0, 15))

		sound_header = tk.Frame(self.card_sound)
		sound_header.pack(fill="x")

		self.lbl_volume = tk.Label(
			sound_header, text="ระดับเสียงระบบ:", font=("Segoe UI", 10)
		)
		self.lbl_volume.pack(side="left")

		self.lbl_vol_val = tk.Label(
			sound_header,
			text=f"{self.volume_level.get()}%",
			font=("Segoe UI", 10, "bold"),
		)
		self.lbl_vol_val.pack(side="right")

		self.slider_volume = tk.Scale(
			self.card_sound,
			from_=0,
			to=100,
			orient="horizontal",
			variable=self.volume_level,
			showvalue=False,
			command=self.update_volume_label,
			bd=0,
			highlightthickness=0,
		)
		self.slider_volume.pack(fill="x", pady=(10, 0))

		self.card_line = tk.LabelFrame(
			self.main_frame,
			text=" 💬 บริการ LINE Notify ",
			font=("Segoe UI", 11, "bold"),
			padx=15,
			pady=15,
			bd=1,
			relief="solid",
		)
		self.card_line.pack(fill="x", pady=(0, 20))

		self.chk_notify = tk.Checkbutton(
			self.card_line,
			text="เปิดใช้งานการส่งข้อความแจ้งเตือน",
			variable=self.notify_enabled,
			font=("Segoe UI", 10),
		)
		self.chk_notify.pack(anchor="w", pady=(0, 10))

		self.lbl_token = tk.Label(
			self.card_line, text="LINE Notify Token:", font=("Segoe UI", 9)
		)
		self.lbl_token.pack(anchor="w")

		self.entry_token = tk.Entry(
			self.card_line,
			textvariable=self.line_token,
			font=("Consolas", 10),
			show="•",
			bd=1,
			relief="solid",
		)
		self.entry_token.pack(fill="x", ipady=6, pady=(5, 5))

		btn_box = tk.Frame(self.main_frame)
		btn_box.pack(fill="x", side="bottom")

		self.btn_save = tk.Button(
			btn_box,
			text="💾 บันทึกการตั้งค่า",
			font=("Segoe UI", 10, "bold"),
			bg="#2563EB",
			fg="white",
			activebackground="#1D4ED8",
			activeforeground="white",
			bd=0,
			padx=20,
			pady=10,
			cursor="hand2",
			command=self.save_config,
		)
		self.btn_save.pack(fill="x")

	def update_volume_label(self, value):
		"""อัปเดตตัวเลขเปอร์เซ็นต์เสียง"""
		self.lbl_vol_val.config(text=f"{int(float(value))}%")

	def on_theme_change(self):
		"""เมื่อเปลี่ยน Radio Button Theme"""
		self.apply_theme(self.current_theme.get())

	def apply_theme(self, theme_name):
		"""สลับสี UI ทั้งหมดตามโทน Light / Dark"""
		theme = self.themes.get(theme_name, self.themes["light"])

		self.root.config(bg=theme["bg"])
		self.main_frame.config(bg=theme["bg"])
		self.header_label.config(bg=theme["bg"], fg=theme["text"])

		for card in (self.card_theme, self.card_sound, self.card_line):
			card.config(
				bg=theme["card"],
				fg=theme["primary"],
				bd=1,
				highlightbackground=theme["border"],
				relief="solid",
			)

		for widget in (
			self.radio_light,
			self.radio_dark,
			self.chk_notify,
			self.lbl_volume,
			self.lbl_vol_val,
			self.lbl_token,
		):
			widget.config(
				bg=theme["card"],
				fg=theme["text"],
				activebackground=theme["card"],
				activeforeground=theme["text"],
				selectcolor=theme["card"],
			)

		self.slider_volume.config(
			bg=theme["card"],
			troughcolor=theme["input_bg"],
			activebackground=theme["primary"],
		)
		self.entry_token.config(
			bg=theme["input_bg"],
			fg=theme["text"],
			insertbackground=theme["text"],
			bd=1,
			relief="solid",
		)


if __name__ == "__main__":
	root = tk.Tk()
	root.withdraw()
	app = ModernSettingsWindow(root)
	app.root.mainloop()
