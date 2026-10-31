from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# ตั้งค่าฟอนต์ภาษาไทยให้ Matplotlib (ใช้ Tahoma บน Windows เพื่อแก้สี่เหลี่ยม)
plt.rcParams['font.family'] = 'Tahoma'
plt.rcParams['axes.unicode_minus'] = False

class AnalyticsModule:
    def get_filtered_history(self, start_date=None, end_date=None, med_name=None):
        """
        ฟังก์ชันเตรียมและกรองข้อมูลประวัติการกินยา
        """
        raw_data = [
            {'date': '25/10/2026', 'med_name': 'Paracetamol', 'status': 'on-time'},
            {'date': '26/10/2026', 'med_name': 'Paracetamol', 'status': 'on-time'},
            {'date': '28/10/2026', 'med_name': 'Paracetamol', 'status': 'on-time'},
            {'date': '30/10/2026', 'med_name': 'Paracetamol', 'status': 'missed'},
        ]
        
        # แปลงข้อความวันที่เป็น datetime object เพื่อให้แกน X เรียงวันที่ถูกต้อง
        for item in raw_data:
            if isinstance(item['date'], str):
                item['date'] = datetime.strptime(item['date'], '%d/%m/%Y')
                
        return raw_data

    def show_medication_timeline(self, start_date=None, end_date=None, med_name=None):
        """
        แสดงกราฟประวัติการกินยาแบบ Timeline แนวนอน (ภาษาไทย)
        """
        filtered_data = self.get_filtered_history(start_date, end_date, med_name)
        
        if not filtered_data:
            print("\n❌ ไม่พบข้อมูลประวัติการกินยาในช่วงเวลาที่ระบุ")
            return

        # ดึงค่าข้อมูล (แกน X = วันที่, แกน Y = ชื่อยา)
        dates = [item['date'] for item in filtered_data]
        meds = [item['med_name'] for item in filtered_data]
        statuses = [item['status'] for item in filtered_data]

        # กำหนดสีตามสถานะ (เขียว = ตรงเวลา, แดง = ข้าม/ลืมกินยา)
        colors = ['#2ecc71' if s == 'on-time' else '#e74c3c' for s in statuses]

        # สร้างรูปกราฟขนาดแนวนอน
        fig, ax = plt.subplots(figsize=(9, 4.5))

        # 1. วาดเส้นและจุดข้อมูลแนวนอน
        ax.plot(dates, meds, color='#bdc3c7', linestyle='--', linewidth=1.5, zorder=1)
        ax.scatter(dates, meds, c=colors, s=130, zorder=2, edgecolors='white', linewidth=1.5)

        # 2. ตั้งค่าชื่อแกนและหัวข้อเป็นภาษาไทย
        ax.set_xlabel("วันที่", fontsize=11, fontweight='bold')
        ax.set_ylabel("ชื่อยา", fontsize=11, fontweight='bold')
        ax.set_title("ประวัติการกินยา (Medication Timeline)", fontsize=13, fontweight='bold', pad=15)

        # 3. จัดรูปแบบวันที่บนแกน X แนวนอน
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
        ax.grid(True, linestyle=':', alpha=0.6, axis='x')
        fig.autofmt_xdate()  # หมุนข้อความวันที่ให้อ่านง่ายขึ้น

        plt.tight_layout()

        # 4. แสดงผลกราฟแบบ Non-blocking (Terminal ไม่ค้าง)
        plt.show(block=False)
        plt.pause(0.1)