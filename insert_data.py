from datetime import datetime, timedelta
from database.db_manager import db

def seed_data():
    if hasattr(db, 'db') and db.db is not None:
        # ดึง Collection จาก MongoDB Atlas
        collections = db.db.list_collection_names()
        
        # เลือก Collection ให้ตรงกับในฐานข้อมูล
        if 'medication_logs' in collections:
            collection = db.db['medication_logs']
        elif 'medications' in collections:
            collection = db.db['medications']
        else:
            collection = db.db['medication_logs']

        today = datetime.now()
        
        # รายการข้อมูลตัวอย่างตามโครงสร้างจริง
        sample_docs = [
            {
                "userId": "a139ebf4-f58f-41f0-88d6-eb5e1a2a191c",
                "medId": "6ae5abdc4bbcb70dd74a2d70",
                "med_name": "Paracetamol 500mg",
                "timesPerDay": ["08:00", "12:00", "18:00", "21:00"],
                "foodRequire": "after",
                "value": 1,
                "status": "on-time",
                "date": (today - timedelta(days=4)).strftime('%d/%m/%Y')
            },
            {
                "userId": "a139ebf4-f58f-41f0-88d6-eb5e1a2a191c",
                "medId": "11297134-84cc-4920-b067-a905feb19066",
                "med_name": "Amoxicillin",
                "timesPerDay": ["08:00", "20:00"],
                "foodRequire": "before",
                "value": 2,
                "status": "on-time",
                "date": (today - timedelta(days=2)).strftime('%d/%m/%Y')
            },
            {
                "userId": "a139ebf4-f58f-41f0-88d6-eb5e1a2a191c",
                "medId": "6ae5abdc4bbcb70dd74a2d70",
                "med_name": "Paracetamol 500mg",
                "timesPerDay": ["08:00"],
                "foodRequire": "after",
                "value": 1,
                "status": "missed",
                "date": today.strftime('%d/%m/%Y')
            }
        ]
        
        # บันทึกลง MongoDB Atlas
        result = collection.insert_many(sample_docs)
        print(f"🟢 บันทึกข้อมูลเข้า MongoDB Atlas สำเร็จ {len(result.inserted_ids)} รายการเรียบร้อยแล้ว!")
    else:
        print("❌ ไม่สามารถเชื่อมต่อฐานข้อมูล MongoDB Atlas ได้")

if __name__ == "__main__":
    seed_data()