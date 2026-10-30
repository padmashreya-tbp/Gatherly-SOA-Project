from flask import request, jsonify
import requests
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import service_app, query, error_response

app = service_app("registration-service")
USER_URL = "http://127.0.0.1:5001"
EVENT_URL = "http://127.0.0.1:5002"
TICKET_URL = "http://127.0.0.1:5004"
NOTIFY_URL = "http://127.0.0.1:5005"

@app.get("/registrations")
def list_registrations():
    return jsonify(query("""SELECT r.*,u.name AS user_name,u.email,e.name AS event_name
                            FROM registrations r JOIN users u ON u.id=r.user_id
                            JOIN events e ON e.id=r.event_id ORDER BY r.id DESC"""))

@app.post("/registrations")
def register():
    d = request.get_json(silent=True) or {}
    user_id, event_id = d.get("user_id"), d.get("event_id")
    if not user_id or not event_id:
        return error_response("user_id and event_id are required")
    try:
        u = requests.get(f"{USER_URL}/users/{int(user_id)}", timeout=4)
        e = requests.get(f"{EVENT_URL}/events/{int(event_id)}", timeout=4)
        if u.status_code != 200:
            return error_response("User service could not find this user", 404)
        if e.status_code != 200:
            return error_response("Event service could not find this event", 404)
        event = e.json()
        if int(event["available_seats"]) <= 0:
            return error_response("This event is full", 409)
        duplicate = query("""SELECT id,status FROM registrations
                             WHERE user_id=%s AND event_id=%s""",
                          (user_id, event_id), "one")
        if duplicate and duplicate["status"] == "confirmed":
            return error_response("You are already registered for this event", 409)
        if duplicate and duplicate["status"] == "cancelled":
            query("UPDATE registrations SET status='confirmed' WHERE id=%s",
                  (duplicate["id"],), fetch="none", commit=True)
            registration_id = duplicate["id"]
        else:
            registration_id = query(
                "INSERT INTO registrations(user_id,event_id) VALUES(%s,%s)",
                (user_id, event_id), "id", True)
        # Update inventory through the event service's database-backed reservation endpoint.
        seat_response = requests.post(f"{EVENT_URL}/events/{int(event_id)}/reserve", timeout=4)
        if seat_response.status_code != 200:
            query("UPDATE registrations SET status='cancelled' WHERE id=%s",
                  (registration_id,), fetch="none", commit=True)
            return error_response(seat_response.json().get("error", "Could not reserve a seat"), 409)
        ticket_response = requests.post(f"{TICKET_URL}/tickets",
                                        json={"registration_id": registration_id}, timeout=4)
        if ticket_response.status_code not in (200, 201):
            return error_response("Registration saved but ticket service failed: " +
                                  ticket_response.text, 502)
        ticket = ticket_response.json().get("ticket_id")
        requests.post(NOTIFY_URL + "/notifications",
                      json={"user_id": int(user_id),
                            "message": f"Registration confirmed for {event['name']}. Ticket: {ticket}",
                            "notification_type":"registration"}, timeout=4)
        return jsonify({"registration_id": registration_id, "user_id": int(user_id),
                        "event_id": int(event_id), "status":"confirmed",
                        "ticket_id": ticket, "message":"Registration successful"}), 201
    except requests.RequestException as exc:
        return error_response("A dependent service is unavailable: " + str(exc), 503)
    except Exception as exc:
        return error_response(str(exc), 500)

@app.post("/registrations/<int:registration_id>/cancel")
def cancel_registration(registration_id):
    reg = query("SELECT * FROM registrations WHERE id=%s", (registration_id,), "one")
    if not reg:
        return error_response("Registration not found", 404)
    if reg["status"] == "cancelled":
        return jsonify({"message":"Registration is already cancelled"})
    query("UPDATE registrations SET status='cancelled' WHERE id=%s",
          (registration_id,), fetch="none", commit=True)
    query("UPDATE tickets SET status='cancelled' WHERE registration_id=%s",
          (registration_id,), fetch="none", commit=True)
    requests.post(f"{EVENT_URL}/events/{reg['event_id']}/release", timeout=4)
    return jsonify({"message":"Registration cancelled and ticket invalidated"})

@app.get("/")
def index():
    return jsonify({"service":"registration-service",
                    "endpoints":["GET /registrations","POST /registrations","POST /registrations/<id>/cancel"]})

if __name__ == "__main__":
    app.run(port=5003, debug=True)
