import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API_BASE_URL = os.environ.get("MEDIC_API_URL", "http://127.0.0.1:5010").rstrip("/")

ERROR_MESSAGES = {
    "content_type_must_be_application_json": "รูปแบบข้อมูลคำขอไม่ถูกต้อง",
    "invalid_request_body": "ข้อมูลคำขอไม่ถูกต้อง",
    "invalid_userName": "ชื่อผู้ใช้ต้องมี 3-30 ตัวอักษร และใช้ได้เฉพาะ a-z, A-Z, 0-9 หรือ _",
    "invalid_userPassword": "รหัสผ่านต้องมีอย่างน้อย 4 ตัวอักษร",
    "userName_is_required": "กรุณากรอกชื่อผู้ใช้",
    "userPassword_is_required": "กรุณากรอกรหัสผ่าน",
    "username_already_exists": "ชื่อผู้ใช้นี้ถูกใช้แล้ว",
    "invalid_credentials": "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง",
    "database_not_configured": "เซิร์ฟเวอร์ยังไม่ได้ตั้งค่าฐานข้อมูล",
    "database_unavailable": "ไม่สามารถเชื่อมต่อฐานข้อมูลได้ในขณะนี้",
    "invalid_user_record": "ข้อมูลบัญชีผู้ใช้ไม่สมบูรณ์",
    "medName_is_required": "กรุณากรอกชื่อยา",
    "medTypeId_is_required": "กรุณาเลือกประเภทยา",
    "unitName_is_required": "กรุณากรอกหน่วยนับ",
    "invalid_BUD": "BUD ต้องเป็นจำนวนวันตั้งแต่ 0 ขึ้นไป",
    "medicine_type_not_found": "ไม่พบประเภทยาที่เลือก",
    "medTypeName_is_required": "กรุณากรอกชื่อประเภทยา",
    "medicine_type_already_exists": "มีประเภทยานี้อยู่แล้ว",
    "medId_is_required": "ไม่พบรหัสยา",
    "medicine_not_found": "ไม่พบรายการยา",
    "type_must_not_be_empty": "กรุณาเลือกประเภทยาที่ถูกต้อง",
    "user_id_is_required": "ไม่พบรหัสผู้ใช้",
    "userId_is_required": "ไม่พบรหัสผู้ใช้",
    "medId_is_required": "กรุณาเลือกยา",
    "invalid_timesPerDay": "กรุณาเลือกช่วงเวลาที่ต้องกินยา",
    "invalid_foodRequire": "ข้อมูลก่อน/หลังอาหารไม่ถูกต้อง",
    "invalid_value": "จำนวนยาต้องมากกว่า 0",
    "user_medicine_already_exists": "ยานี้อยู่ในรายการของคุณแล้ว",
    "user_medicine_not_found": "ไม่พบรายการยาของคุณ",
}


class APIRequestError(Exception):
    """An API request failed or returned an unsuccessful response."""


def api_request(path, payload=None, method="POST"):
    headers = {}
    body = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(payload).encode("utf-8")
    request = Request(
        f"{API_BASE_URL}{path}",
        data=body,
        headers=headers,
        method=method,
    )

    try:
        with urlopen(request, timeout=5) as response:
            response_body = response.read()
    except HTTPError as error:
        response_body = error.read()
        try:
            error_data = json.loads(response_body)
        except (UnicodeDecodeError, json.JSONDecodeError) as parse_error:
            raise APIRequestError("เซิร์ฟเวอร์ตอบกลับข้อมูลที่อ่านไม่ได้") from parse_error
        if isinstance(error_data, dict):
            error_code = error_data.get("error")
            message = (
                ERROR_MESSAGES.get(error_code, error_data.get("message"))
                if isinstance(error_code, str)
                else error_data.get("message")
            )
        else:
            message = None
        if not isinstance(message, str):
            message = f"คำขอไม่สำเร็จ (HTTP {error.code})"
        raise APIRequestError(message) from error
    except (URLError, TimeoutError) as error:
        raise APIRequestError(
            "เชื่อมต่อ API ไม่ได้ กรุณาตรวจสอบว่าเซิร์ฟเวอร์กำลังทำงาน"
        ) from error

    try:
        data = json.loads(response_body)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise APIRequestError("เซิร์ฟเวอร์ตอบกลับข้อมูลที่อ่านไม่ได้") from error
    if not isinstance(data, (dict, list)):
        raise APIRequestError("รูปแบบข้อมูลตอบกลับจากเซิร์ฟเวอร์ไม่ถูกต้อง")
    return data
