import sys
import os
from datetime import datetime, date, timedelta

import matplotlib
matplotlib.use('TkAgg')  # บังคับใช้ backend TkAgg สำหรับ GUI บน Windows
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import db

# ตั้งค่าฟอนต์ภาษาไทยบน Matplotlib
plt.rcParams['font.family'] = 'Tahoma'
plt.rcParams['axes.unicode_minus'] = False

class AnalyticsModule:
    def __init__(self):
        pass

    def _get_active_collection(self):
        """ดึง Collection medication_logs หรือ medications จาก DB"""
        if hasattr(db, 'db') and db.db is not None:
            try:
                collections = db.db.list_collection_names()
                if 'medication_logs' in collections:
                    return db.db['medication_logs']
                elif 'medications' in collections:
                    return db.db['medications']
                elif collections:
                    return db.db[collections[0]]
            except Exception:
                pass
        
        if hasattr(db, 'logs') and db.logs is not None:
            return db.logs
        if hasattr(db, 'medications') and db.medications is not None:
            return db.medications
        return None

    def _normalize_datetime(self, val):
        """แปลงค่าวันที่ทุกรูปแบบ (date, str, datetime) ให้เป็น datetime object เพื่อความปลอดภัย"""
        if isinstance(val, datetime):
            return val
        if isinstance(val, date):
            return datetime.combine(val, datetime.min.time())
        if isinstance(val, str):
            for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y'):
                try:
                    return datetime.strptime(val, fmt)
                except ValueError:
                    pass
        return datetime.now()

    def get_special_alerts(self):
        """ดึงรายการแจ้งเตือนพิเศษ (เมนู 1)"""
        alerts = []
        col = self._get_active_collection()
        if col is not None:
            try:
                cursor = col.find()
                for doc in cursor:
                    name = doc.get('med_name', doc.get('name', doc.get('medicine_name', 'ไม่ระบุชื่อยา')))
                    stock = doc.get('stock_remaining', doc.get('stock', doc.get('qty', None)))
                    if stock is not None:
                        try:
                            if int(stock) <= 5:
                                alerts.append(f"⚠️ ยา {name} เหลือเพียง {stock} ชิ้น (ใกล้หมดสต็อก)")
                        except (ValueError, TypeError):
                            pass
            except Exception:
                pass

        if not alerts:
            alerts.append("✅ ไม่พบรายการแจ้งเตือนพิเศษ (สต็อกยาอยู่ในระดับปกติ)")
        return alerts

    def get_filtered_history(self, start_date=None, end_date=None, med_name=None):
        """ดึงประวัติการกินยาจาก Atlas"""
        col = self._get_active_collection()
        raw_docs = []

        if col is not None:
            try:
                raw_docs = list(col.find())
            except Exception:
                raw_docs = []

        # หากใน Database ยังไม่มีข้อมูล ให้สร้างข้อมูลตัวอย่างชั่วคราวเพื่อใช้วาดกราฟทดสอบ
        if not raw_docs:
            today = datetime.now()
            raw_docs = [
                {"med_name": "Paracetamol 500mg", "date": (today - timedelta(days=5)).strftime('%d/%m/%Y'), "status": "on-time"},
                {"med_name": "Amoxicillin", "date": (today - timedelta(days=3)).strftime('%d/%m/%Y'), "status": "on-time"},
                {"med_name": "Vitamin C", "date": (today - timedelta(days=1)).strftime('%d/%m/%Y'), "status": "missed"},
                {"med_name": "Paracetamol 500mg", "date": today.strftime('%d/%m/%Y'), "status": "on-time"}
            ]

        start_dt = self._normalize_datetime(start_date) if start_date else None
        end_dt = self._normalize_datetime(end_date) if end_date else None

        filtered = []
        for doc in raw_docs:
            item_name = doc.get('med_name', doc.get('name', doc.get('medicine_name', 'ไม่ระบุชื่อยา')))
            raw_date = doc.get('date', doc.get('expire_date', doc.get('timestamp')))
            item_date = self._normalize_datetime(raw_date)
            item_status = doc.get('status', 'on-time')

            if med_name and med_name.strip().lower() not in item_name.lower():
                continue

            if start_dt and item_date < start_dt:
                continue
            if end_dt and item_date > end_dt:
                continue

            filtered.append({
                'date': item_date,
                'med_name': item_name,
                'status': item_status
            })

        filtered.sort(key=lambda x: x['date'])
        return filtered

    def show_medication_timeline(self, start_date=None, end_date=None, med_name=None):
        """สร้างและวาดกราฟ Timeline ประวัติการกินยา"""
        records = self.get_filtered_history(start_date, end_date, med_name)

        if not records:
            print("\n❌ ไม่พบข้อมูลประวัติการกินยาตามเงื่อนไขที่เลือก")
            return

        dates = [item['date'] for item in records]
        meds = [item['med_name'] for item in records]
        statuses = [item['status'] for item in records]

        # สีแสดงสถานะ: เขียว = ตรงเวลา / แดง = ข้าม/ลืม
        colors = ['#2ecc71' if s == 'on-time' else '#e74c3c' for s in statuses]

        fig, ax = plt.subplots(figsize=(9.5, 4.8))
        ax.plot(dates, meds, color='#bdc3c7', linestyle='--', linewidth=1.5, zorder=1)
        ax.scatter(dates, meds, c=colors, s=140, zorder=2, edgecolors='white', linewidth=1.5)

        ax.set_xlabel("วันที่", fontsize=11, fontweight='bold')
        ax.set_ylabel("ชื่อยา", fontsize=11, fontweight='bold')
        ax.set_title("ประวัติการกินยา (Medication Timeline)", fontsize=13, fontweight='bold', pad=15)

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
        ax.grid(True, linestyle=':', alpha=0.6, axis='x')
        fig.autofmt_xdate()

        plt.tight_layout()

        # ดึงหน้าต่างกราฟขึ้นมาอยู่หน้าสุด
        try:
            manager = plt.get_current_fig_manager()
            manager.window.attributes('-topmost', 1)
            manager.window.attributes('-topmost', 0)
        except Exception:
            pass

        print("\n📊 กำลังแสดงหน้าต่างกราฟประวัติการกินยา (ปิดหน้าต่างกราฟเพื่อกลับสู่เมนูหลัก)...")
        plt.show()  # ล็อกหน้าต่างกราฟค้างไว้จนกว่าผู้ใช้จะกดปิด

    def show_dashboard(self):
        records = self.get_filtered_history()
        total_records = len(records)
        
        print("\n=== 📊 แดชบอร์ดสรุปสถิติการกินยา ===")
        
        if total_records == 0:
            print("⚠️ ไม่พบข้อมูลประวัติการกินยาในระบบ")
            return

        # คำนวณสถานะการกินยา
        on_time_count = sum(1 for r in records if r.get('status') == 'on-time')
        missed_count = sum(1 for r in records if r.get('status') == 'missed')
        
        # คำนวณอัตรา Adherence Rate (%)
        adherence_rate = (on_time_count / total_records) * 100

        print(f"📦 รายการประวัติทั้งหมดในระบบ: {total_records} รายการ")
        print(f"✅ กินตรงเวลา (On-time):        {on_time_count} ครั้ง")
        print(f"❌ ข้าม/ลืมกิน (Missed):          {missed_count} ครั้ง")
        print(f"🎯 อัตราความร่วมมือ (Adherence Rate): {adherence_rate:.2f}%")
        print("------------------------------------------")