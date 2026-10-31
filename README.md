# medic-program

## API service (Flask scaffold)

Install the API dependency from the project root:

```bash
python -m pip install -r requirements.txt
```

The service listens on `http://127.0.0.1:5010` by default.

### Desktop app

Install the project dependencies, start the API as described above, then launch
the Tkinter desktop app from the project root:

```powershell
python -m app.service
```

The app supports signup and login, then shows the `userId`, `userName`, and
`userRole` returned by the API. Set `MEDIC_API_URL` if the API is hosted at a
different URL; the default is `http://127.0.0.1:5010`.
Users with the `admin` role are taken to the medicine administration screen,
where they can add and delete medicines and medicine types using `/med` and
`/med/type`.
On Windows, the user medicine screen sends audible native notifications at
08:00, 12:00, 16:00, and 20:00 for selected medicine periods while the app is
running. The page shows a fixed four-period dose summary, the full daily
medicine list with removal controls, and the add-medicine form. Use
**ทดสอบการแจ้งเตือน** to check the configured times and next reminder.

Create a `.env` file in the project root and set `MONGODB_URI` there:

```dotenv
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>/
```

The service loads this file automatically. Environment variables already set
outside the file take precedence. Start the API with:

```powershell
python -m api.service
```

Each endpoint is implemented in its own module under `api/` (`health.py`,
`auth_signup.py`, `auth_login.py`, `auth_logout.py`, `medicine_type.py`, and
`medicines.py`, and `user_medicines.py`). The central `api/service.py`
registers these routes; shared MongoDB, password, and request helpers are in
`database.py`, `passwords.py`, and `request_helpers.py`.

The login endpoint uses the `auth.users` collection:

```http
POST /auth/login
Content-Type: application/json
```

```json
{
  "userName": "your-user-name",
  "userPassword": "your-password"
}
```

On success it returns `userId`, `userName`, and `userRole`. Invalid credentials
return `401`; missing MongoDB configuration or an unavailable database returns
`503`. Existing plain-text passwords are upgraded to Werkzeug password hashes
after a successful login.

### Signup

`POST /auth/signup` accepts `userName` (3-30 letters, numbers, or underscores)
and `userPassword` (at least 4 characters). Usernames are unique, passwords
are stored as Werkzeug hashes, and new accounts always receive the `user` role.
Successful signup returns HTTP `200` with `message`, `userId`, `userName`, and
`userRole`.

### Logout

`POST /auth/logout` accepts a `userId` and returns a successful acknowledgement.
This endpoint is stateless: it does not revoke a login session or token, because
the current API does not issue sessions or tokens. The client must clear its
local login state.

All `/auth` endpoint attempts are recorded in the `auth.user_logs` collection
with `userId`, `action`, `result`, and a Unix-seconds `timestamp`. Passwords and
other credentials are never included in audit records. If MongoDB cannot store
an audit record, the endpoint responds with `503` rather than reporting the
action as successful.

### Medicine types

Medicine types are stored in the `medicine.medicine_type` collection.
`POST /med/type` accepts `{"medTypeName": "..."}` and returns the created
`medTypeId` and `medTypeName` with HTTP `201`; duplicate names return `409`.
`GET /med/type` returns an array of `{medTypeId, medTypeName}` objects.
`DELETE /med/type` accepts `{"medTypeId": "..."}` and deletes that type;
unknown IDs return `404`.

### Medicines

Medicines are stored in the `medicine.medicines` collection. `POST /med`
accepts `medName`, `medTypeId`, `unitName`, and `BUD` (either `null` or a
non-negative integer number of days), validates that the medicine type exists,
and returns `medId`, `medName`, `medTypeId`, `unitName`, and `BUD` with HTTP
`201`.
`GET /med` returns an array with those fields; pass `?type=<medTypeId>` to
filter by medicine type. `DELETE /med` accepts `{"medId": "..."}`; unknown IDs
return `404`. The MongoDB `_id` is exposed in the API as `medId`.

### User medicines

User medicine records are stored in `mymed.user_medicine`. `GET /user/med`
requires `?user_id=<userId>` and returns an array of `medId`, `timesPerDay`,
`foodRequire`, and `value`. `POST /user/med` accepts `userId`, `medId`, `value`
(positive dose quantity), `timesPerDay`, and `foodRequire`; `timesPerDay` is
an array of unique values from `1` to `4` (morning, midday, evening, and
bedtime); an empty array means take as needed when symptoms occur. `foodRequire`
must be `"before"`, `"after"`, or `null`. Duplicate user/medicine pairs return
`409`. `DELETE /user/med` accepts `userId` and `medId` in the JSON body.

| Method | Path | Status |
| --- | --- | --- |
| `GET` | `/health` | Implemented |
| `POST` | `/auth/signup` | Implemented |
| `POST` | `/auth/login` | Implemented |
| `POST` | `/auth/logout` | Implemented (stateless acknowledgement) |
| `POST` | `/med/type` | Implemented |
| `GET` | `/med/type` | Implemented |
| `DELETE` | `/med/type` | Implemented |
| `POST` | `/med` | Implemented |
| `GET` | `/med` | Implemented |
| `DELETE` | `/med` | Implemented |
| `GET` | `/user/med` | Implemented |
| `POST` | `/user/med` | Implemented |
| `DELETE` | `/user/med` | Implemented |
