import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

class MockCollection:
    """คลาสจำลองข้อมูลสำรองกรณีการเชื่อมต่อ Cloud DB มีปัญหา"""
    def find(self, query=None):
        return [
            {
                "med_name": "Paracetamol 500mg", 
                "date": "01/11/2026", 
                "status": "on-time", 
                "stock_remaining": 3
            },
            {
                "med_name": "Amoxicillin", 
                "date": "03/11/2026", 
                "status": "on-time", 
                "stock_remaining": 12
            },
            {
                "med_name": "Vitamin C", 
                "date": "05/11/2026", 
                "status": "missed", 
                "stock_remaining": 20
            }
        ]

class DatabaseManager:
    def __init__(self):
        # URI เชื่อมต่อ MongoDB Atlas ระบุ Database mymed ด้านท้าย
        self.uri = "mongodb+srv://69030263_db_user:QsZ1mmRGYCCJhD1t@project1.wshqjbc.mongodb.net/mymed?retryWrites=true&w=majority"
        self.db_name = "mymed"
        
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            
            self.db = self.client[self.db_name]
            # อ้างอิง Collection medication_logs ตามที่ตั้งค่าใน Atlas
            self.logs = self.db['medication_logs']
            self.medications = self.db['medications']
            print("🟢 [DatabaseManager] เชื่อมต่อ MongoDB Atlas สำเร็จแล้ว!")
            
        except (ConnectionFailure, ServerSelectionTimeoutError, Exception) as e:
            print(f"⚠️ [DatabaseManager] เชื่อมต่อ Cloud DB ไม่สำเร็จ ({e}) -> สลับไปใช้ Mock Data")
            self.db = None
            self.logs = MockCollection()
            self.medications = MockCollection()

# Singleton Instance สำหรับดึงไปใช้ทั้งโปรเจกต์
db = DatabaseManager()