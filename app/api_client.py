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
}


class APIRequestError(Exception):
    """An API request failed or returned an unsuccessful response."""


def api_request(path, payload):
    request = Request(
        f"{API_BASE_URL}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
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
    if not isinstance(data, dict):
        raise APIRequestError("รูปแบบข้อมูลตอบกลับจากเซิร์ฟเวอร์ไม่ถูกต้อง")
    return data
