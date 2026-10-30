from flask import jsonify
from common import service_app, query, error_response

app = service_app("ticket-service")

@app.get("/tickets")
def list_tickets():
    return jsonify(query("""SELECT t.id,t.ticket_id,t.registration_id,t.status,t.created_at,
                           r.user_id,r.event_id,e.name AS event_name
                           FROM tickets t JOIN registrations r ON r.id=t.registration_id
                           JOIN events e ON e.id=r.event_id ORDER BY t.id DESC"""))

@app.get("/tickets/<ticket_code>")
def get_ticket(ticket_code):
    row = query("""SELECT t.id,t.ticket_id,t.registration_id,t.status,t.created_at,
                   r.user_id,r.event_id,e.name AS event_name,e.event_date,e.venue
                   FROM tickets t JOIN registrations r ON r.id=t.registration_id
                   JOIN events e ON e.id=r.event_id WHERE t.ticket_id=%s""",
                (ticket_code,), "one")
    return (jsonify(row), 200) if row else error_response("Ticket not found", 404)

@app.post("/tickets")
def create_ticket():
    from flask import request
    import uuid
    d = request.get_json(silent=True) or {}
    registration_id = d.get("registration_id")
    if not registration_id:
        return error_response("registration_id is required")
    reg = query("SELECT * FROM registrations WHERE id=%s", (registration_id,), "one")
    if not reg or reg["status"] != "confirmed":
        return error_response("A confirmed registration is required", 400)
    existing = query("SELECT ticket_id FROM tickets WHERE registration_id=%s",
                     (registration_id,), "one")
    if existing:
        return jsonify({"ticket_id": existing["ticket_id"], "message": "Ticket already exists"})
    code = "GT-" + uuid.uuid4().hex[:10].upper()
    query("INSERT INTO tickets(ticket_id,registration_id) VALUES(%s,%s)",
          (code, registration_id), fetch="id", commit=True)
    return jsonify({"ticket_id": code, "registration_id": registration_id,
                    "status": "valid", "message": "Ticket generated"}), 201

@app.get("/")
def index():
    return jsonify({"service":"ticket-service","endpoints":["GET /tickets","GET /tickets/<ticket_code>","POST /tickets"]})

if __name__ == "__main__":
    app.run(port=5004, debug=True)
