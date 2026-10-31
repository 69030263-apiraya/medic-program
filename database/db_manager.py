class MockCollection:
    def find(self, query=None):
        # จำลองข้อมูลยาในระบบสำหรับทดสอบแจ้งเตือนสต็อกและวันหมดอายุ
        return [
            {"name": "Paracetamol 500mg", "stock_remaining": 3, "expire_date": "2026-11-15"},
            {"name": "Amoxicillin", "stock_remaining": 12, "expire_date": "2026-11-05"},
            {"name": "Vitamin C", "stock_remaining": 20, "expire_date": "2027-05-20"}
        ]

class DatabaseManager:
    def __init__(self):
        self.medications = MockCollection()
        self.logs = MockCollection()
        print("🟢 ใช้งานโหมดข้อมูลจำลอง (ไม่ได้เชื่อมต่อ MongoDB จริงจ้ะ)")

db = DatabaseManager()