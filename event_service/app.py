from flask import request, jsonify
from common import service_app, query, error_response

app = service_app("event-service")

@app.get("/events")
def list_events():
    return jsonify(query("SELECT * FROM events ORDER BY event_date ASC"))

@app.get("/events/<int:event_id>")
def get_event(event_id):
    row = query("SELECT * FROM events WHERE id=%s", (event_id,), "one")
    return (jsonify(row), 200) if row else error_response("Event not found", 404)

@app.post("/events")
def create_event():
    d = request.get_json(silent=True) or {}
    required = ["name", "event_date", "venue"]
    if not all(str(d.get(k, "")).strip() for k in required):
        return error_response("name, event_date and venue are required")
    try:
        capacity = int(d.get("capacity", 50))
        if capacity < 1:
            return error_response("capacity must be at least 1")
        event_id = query(
            """INSERT INTO events(name,description,event_date,venue,capacity,available_seats)
               VALUES(%s,%s,%s,%s,%s,%s)""",
            (d["name"].strip(), d.get("description", ""), d["event_date"],
             d["venue"].strip(), capacity, capacity), "id", True)
        return jsonify({"id": event_id, "message": "Event created"}), 201
    except Exception as exc:
        return error_response(str(exc), 400)

@app.put("/events/<int:event_id>")
def update_event(event_id):
    d = request.get_json(silent=True) or {}
    existing = query("SELECT * FROM events WHERE id=%s", (event_id,), "one")
    if not existing:
        return error_response("Event not found", 404)
    allowed = ["name", "description", "event_date", "venue"]
    values = {k: d.get(k, existing[k]) for k in allowed}
    try:
        query("""UPDATE events SET name=%s,description=%s,event_date=%s,venue=%s
                 WHERE id=%s""",
              (values["name"], values["description"], values["event_date"],
               values["venue"], event_id), fetch="none", commit=True)
        return jsonify({"message": "Event updated"})
    except Exception as exc:
        return error_response(str(exc), 400)

@app.post("/events/<int:event_id>/reserve")
def reserve_seat(event_id):
    # Atomic update prevents overbooking when requests arrive close together.
    conn = None
    try:
        from common import get_pool
        conn = get_pool().get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""UPDATE events SET available_seats=available_seats-1
                       WHERE id=%s AND available_seats > 0""", (event_id,))
        if cur.rowcount != 1:
            conn.rollback()
            return error_response("Event not found or no seats remain", 409)
        conn.commit()
        return jsonify({"message":"Seat reserved","event_id":event_id})
    except Exception as exc:
        if conn:
            conn.rollback()
        return error_response(str(exc), 500)
    finally:
        if conn:
            cur.close()
            conn.close()

@app.post("/events/<int:event_id>/release")
def release_seat(event_id):
    query("""UPDATE events SET available_seats=LEAST(capacity,available_seats+1)
             WHERE id=%s""", (event_id,), fetch="none", commit=True)
    return jsonify({"message":"Seat released","event_id":event_id})

@app.get("/")
def index():
    return jsonify({"service":"event-service","endpoints":["GET /events","POST /events","PUT /events/<id>"]})

if __name__ == "__main__":
    app.run(port=5002, debug=True)
