import datetime
import matplotlib.pyplot as plt
from database.db_manager import db

# ตั้งค่าฟอนต์ภาษาไทยสำหรับ Windows
plt.rcParams['font.family'] = 'Tahoma'

class AnalyticsModule:
    # ---------------------------------------------------------
    # 1. Widget / Banner แจ้งเตือนพิเศษบนหน้าหลัก
    # ---------------------------------------------------------
    def get_special_alerts(self):
        alerts = []
        today = datetime.date.today()
        thirty_days_later = today + datetime.timedelta(days=30)
        
        print("\n==========================================")
        print("🔔 WIDGET / BANNER แจ้งเตือนพิเศษบนหน้าหลัก")
        print("==========================================")
        
        all_meds = db.medications.find()
        for med in all_meds:
            if med.get("stock_remaining", 0) < 5:
                alerts.append(f"⚠️ [คลังยา] เตือน: ยา '{med['name']}' ใกล้หมดสต็อก! (เหลือ {med['stock_remaining']} เม็ด)")

        for med in all_meds:
            if "expire_date" in med:
                exp_date = datetime.datetime.strptime(med["expire_date"], "%Y-%m-%d").date()
                if today <= exp_date <= thirty_days_later:
                    days_left = (exp_date - today).days
                    alerts.append(f"⏰ [หมดอายุ] เตือน: ยา '{med['name']}' จะหมดอายุภายใน {days_left} วัน ({med['expire_date']})")

        if not alerts:
            alerts.append("✅ ปกติ: ไม่มีแจ้งเตือนพิเศษในขณะนี้")
            
        return alerts

    # ---------------------------------------------------------
    # 2. หน้าประวัติการกินยา (History View) - ตกแต่งสวยงาม
    # ---------------------------------------------------------
    def show_medication_timeline(self, start_date=None, end_date=None, med_name=None):
        print("\n==========================================")
        print("📅 หน้าประวัติการกินยา (HISTORY VIEW)")
        print("==========================================")

        today = datetime.date.today()
        all_logs = [
            {"date": today - datetime.timedelta(days=6), "med_name": "Paracetamol", "status": "On Time"},
            {"date": today - datetime.timedelta(days=5), "med_name": "Paracetamol", "status": "On Time"},
            {"date": today - datetime.timedelta(days=4), "med_name": "Amoxicillin", "status": "Missed"},
            {"date": today - datetime.timedelta(days=3), "med_name": "Paracetamol", "status": "On Time"},
            {"date": today - datetime.timedelta(days=2), "med_name": "Amoxicillin", "status": "On Time"},
            {"date": today - datetime.timedelta(days=1), "med_name": "Paracetamol", "status": "Missed"},
            {"date": today, "med_name": "Amoxicillin", "status": "On Time"},
        ]

        filtered_logs = all_logs

        if start_date and end_date:
            filtered_logs = [l for l in filtered_logs if start_date <= l["date"] <= end_date]
            print(f"🔍 กรองช่วงวันที่: {start_date.strftime('%d/%m/%Y')} ถึง {end_date.strftime('%d/%m/%Y')}")

        if med_name:
            filtered_logs = [l for l in filtered_logs if l["med_name"].lower() == med_name.lower()]
            print(f"🔍 กรองตามชื่อยา: {med_name}")

        if not filtered_logs:
            print("❌ ไม่พบข้อมูลประวัติการกินยาตามเงื่อนไขที่ระบุ")
            return

        for log in filtered_logs:
            date_str = log["date"].strftime("%d/%m/%Y")
            icon = "🟢" if log["status"] == "On Time" else "🔴"
            status_text = "กินตรงเวลา" if log["status"] == "On Time" else "ข้าม/ลืมกินยา"
            print(f"{icon} {date_str} [{log['med_name']}] : {status_text}")

        # --- วาดกราฟ Timeline ตกแต่งสวยงาม ---
        dates = [log["date"].strftime("%d/%m") for log in filtered_logs]
        statuses = [log["status"] for log in filtered_logs]
        
        # สีพาสเทล มินิมอล
        color_map = {'On Time': '#2ECC71', 'Missed': '#E74C3C'}
        colors = [color_map[s] for s in statuses]

        fig, ax = plt.subplots(figsize=(10, 3.8), facecolor='#F8F9FA')
        ax.set_facecolor('#F8F9FA')

        # เส้นเชื่อม Timeline
        ax.plot(dates, [1]*len(dates), color='#BDC3C7', linestyle='-', linewidth=3, zorder=1)

        # จุดวงกลมใหญ่พร้อมขอบขาว
        ax.scatter(dates, [1]*len(dates), c=colors, s=700, edgecolors='white', linewidths=3, zorder=3)

        # ใส่ข้อความกำกับ
        for i, log in enumerate(filtered_logs):
            label = "ตรงเวลา" if log["status"] == "On Time" else "ข้าม/ลืม"
            bg_color = '#E8F8F5' if log["status"] == "On Time" else '#FDEDEC'
            
            # ป้ายข้อความสวยงาม
            ax.text(i, 1.12, f"{log['med_name']}\n({label})", ha='center', va='bottom', 
                    fontsize=9, fontweight='bold', color=colors[i],
                    bbox=dict(boxstyle='round,pad=0.4', facecolor=bg_color, edgecolor=colors[i], alpha=0.9))

        # ปรับแต่งองค์ประกอบกราฟ
        ax.set_title('📅 Timeline ประวัติการกินยาย้อนหลัง', fontsize=14, fontweight='bold', color='#2C3E50', pad=35)
        ax.set_ylim(0.8, 1.4)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color('#BDC3C7')
        ax.get_yaxis().set_visible(False)
        
        plt.tight_layout()
        plt.show()

    # ---------------------------------------------------------
    # 3. หน้า Dashboard สถิติ (Donut Chart มินิมอล)
    # ---------------------------------------------------------
    def show_dashboard(self):
        print("\n==========================================")
        print("📊 หน้า DASHBOARD สถิติความสม่ำเสมอ")
        print("==========================================")

        total_doses = 20
        on_time_doses = 15
        missed_doses = total_doses - on_time_doses

        adherence_rate = (on_time_doses / total_doses) * 100
        missed_rate = 100 - adherence_rate

        print(f"📈 จำนวนครั้งที่กินตรงเวลา: {on_time_doses}/{total_doses} ครั้ง")
        print(f"🎯 เปอร์เซ็นต์ความสม่ำเสมอ (Adherence Rate): {adherence_rate:.1f}%")

        # --- วาดกราฟ Donut Chart ดีไซน์พรีเมียม ---
        labels = ['กินตรงเวลา', 'ข้าม/ลืมกิน']
        sizes = [adherence_rate, missed_rate]
        colors = ['#2ECC71', '#E74C3C']

        fig, ax = plt.subplots(figsize=(6.5, 6.5), facecolor='#F8F9FA')
        
        wedges, texts, autotexts = ax.pie(
            sizes, 
            labels=labels, 
            colors=colors, 
            autopct='%1.1f%%', 
            startangle=90, 
            pctdistance=0.75,
            explode=(0.03, 0),
            textprops=dict(fontsize=11, fontweight='bold', color='#2C3E50'),
            wedgeprops=dict(width=0.4, edgecolor='white', linewidth=3) # แปลงเป็น Donut
        )

        # ตกแต่งเปอร์เซ็นต์ข้างใน
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(11)
            autotext.set_weight('bold')

        # ใส่ข้อความตรงกลางวงกลม Donut
        ax.text(0, 0, f"Adherence\n{adherence_rate:.0f}%", ha='center', va='center', 
                fontsize=16, fontweight='bold', color='#2C3E50')

        ax.set_title('📊 สถิติความสม่ำเสมอในการกินยา\n(Medication Adherence Rate)', 
                     fontsize=14, fontweight='bold', color='#2C3E50', pad=20)
        
        plt.tight_layout()
        plt.show()