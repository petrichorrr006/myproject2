# API Testing Guide (Postman / cURL)

Base URL (run server with `python manage.py runserver`): **http://127.0.0.1:8000**

---

## 1. Slots API — `/api/slots/` and `/api/slots/<id>/`

| Method | URL | Description |
|--------|-----|-------------|
| **GET** | `/api/slots/` | List all time slots |
| **GET** | `/api/slots/1/` | Get one slot by id |
| **POST** | `/api/slots/` | Create a slot (body: `provider_id`, `start_time`, `end_time`) |
| **PUT** | `/api/slots/1/` | Update a slot (body: `is_booked`, optional `start_time`, `end_time`) |
| **DELETE** | `/api/slots/1/` | Delete a slot |

**POST body example (create slot):**
```json
{
  "provider_id": 1,
  "start_time": "2025-02-10T14:00:00",
  "end_time": "2025-02-10T14:30:00"
}
```

**PUT body example (update slot):**
```json
{
  "is_booked": true
}
```

---

## 2. Providers API — `/api/providers/` and `/api/providers/<id>/`

| Method | URL | Description |
|--------|-----|-------------|
| **GET** | `/api/providers/` | List all providers |
| **GET** | `/api/providers/1/` | Get one provider by id |
| **POST** | `/api/providers/` | Create a provider (body: `user_id`, `specialization`) |
| **PUT** | `/api/providers/1/` | Update a provider (body: `specialization`) |
| **DELETE** | `/api/providers/1/` | Delete a provider |

**POST body example:**
```json
{
  "user_id": 1,
  "specialization": "Cardiologist"
}
```

---

## 3. Bookings API — `/api/bookings/` and `/api/bookings/<id>/`

| Method | URL | Description |
|--------|-----|-------------|
| **GET** | `/api/bookings/` | List all bookings |
| **GET** | `/api/bookings/1/` | Get one booking by id |
| **POST** | `/api/bookings/` | Create a booking (body: `client_id`, `slot_id`); marks slot as booked |
| **PUT** | `/api/bookings/1/` | Update a booking (body: `slot_id` and/or `client_id`) |
| **DELETE** | `/api/bookings/1/` | Delete a booking; marks slot as available again |

**POST body example:**
```json
{
  "client_id": 1,
  "slot_id": 1
}
```

---

## Quick cURL examples

```bash
# GET all slots
curl http://127.0.0.1:8000/api/slots/

# GET one slot
curl http://127.0.0.1:8000/api/slots/1/

# POST create slot (ensure provider_id exists)
curl -X POST http://127.0.0.1:8000/api/slots/ \
  -H "Content-Type: application/json" \
  -d '{"provider_id":1,"start_time":"2025-02-10T14:00:00","end_time":"2025-02-10T14:30:00"}'

# PUT update slot
curl -X PUT http://127.0.0.1:8000/api/slots/1/ \
  -H "Content-Type: application/json" \
  -d '{"is_booked":true}'

# DELETE slot
curl -X DELETE http://127.0.0.1:8000/api/slots/1/

# GET all providers
curl http://127.0.0.1:8000/api/providers/

# GET all bookings
curl http://127.0.0.1:8000/api/bookings/
```

In **Postman**: create a collection, set base URL to `http://127.0.0.1:8000`, and add requests for each method/endpoint above. For POST/PUT, set body to **raw** and **JSON**.
