from flask import request, jsonify
from common import service_app, query, error_response

app = service_app("notification-service")

@app.get("/notifications")
def list_notifications():
    user_id = request.args.get("user_id", type=int)
    if user_id:
        rows = query("SELECT * FROM notifications WHERE user_id=%s ORDER BY id DESC",
                     (user_id,))
    else:
        rows = query("SELECT * FROM notifications ORDER BY id DESC")
    return jsonify(rows)

@app.post("/notifications")
def create_notification():
    d = request.get_json(silent=True) or {}
    user_id, message = d.get("user_id"), str(d.get("message", "")).strip()
    kind = d.get("notification_type", "registration")
    if not user_id or not message:
        return error_response("user_id and message are required")
    try:
        nid = query("""INSERT INTO notifications(user_id,message,notification_type)
                       VALUES(%s,%s,%s)""", (user_id, message, kind), "id", True)
        return jsonify({"id": nid, "message": "Notification created"}), 201
    except Exception as exc:
        return error_response(str(exc), 400)

@app.patch("/notifications/<int:notification_id>/read")
def mark_read(notification_id):
    query("UPDATE notifications SET is_read=TRUE WHERE id=%s",
          (notification_id,), fetch="none", commit=True)
    return jsonify({"message":"Notification marked as read"})

@app.get("/")
def index():
    return jsonify({"service":"notification-service","endpoints":["GET /notifications","POST /notifications"]})

if __name__ == "__main__":
    app.run(port=5005, debug=True)
