from datetime import datetime, timedelta
from modules.analytics import AnalyticsModule

def main():
    analytics = AnalyticsModule()

    while True:
        print("\n======================================")
        print(" [1] 🔔 ดู Widget/Banner การแจ้งเตือนพิเศษ")
        print(" [2] 📅 ดูหน้าประวัติการกินยา (History View - ทั้งหมด)")
        print(" [3] 🔍 กรองประวัติการกินยา (Filter ตามยา/วันที่)")
        print(" [4] 📊 ดูหน้า Dashboard สถิติ (Adherence Rate%)")
        print(" [0] 🚪 ออกจากโปรแกรม")
        print("======================================")

        choice = input("👉 กรุณาเลือกเมนูที่ต้องการ (0-4): ").strip()

        if choice == '1':
            alerts = analytics.get_special_alerts()
            print("\n--- 🔔 รายการแจ้งเตือนพิเศษ ---")
            for alert in alerts:
                print(f"  {alert}")

        elif choice == '2':
            # เรียกแสดงกราฟประวัติทั้งหมด
            analytics.show_medication_timeline()

        elif choice == '3':
            print("\n--- 🔍 ระบบกรองข้อมูลประวัติการกินยา ---")
            med_name = input("พิมพ์ชื่อยาที่ต้องการกรอง (กด Enter ถ้าไม่ต้องการระบุ): ").strip()
            med_input = med_name if med_name else None

            analytics.show_medication_timeline(med_name=med_input)

        elif choice == '4':
            analytics.show_dashboard()

        elif choice == '0':
            print("\nขอบคุณที่ใช้งานระบบจ้ะ! 👋😊")
            break
        else:
            print("\n❌ ตัวเลือกไม่ถูกต้อง กรุณาพิมพ์หมายเลข 0-4 นะจ๊ะ")

if __name__ == "__main__":
    main()