from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from common import service_app, query, error_response

app = service_app("user-service")

@app.get("/users")
def list_users():
    rows = query("SELECT id,name,email,student_id,created_at FROM users ORDER BY id DESC")
    return jsonify(rows)

@app.get("/users/<int:user_id>")
def get_user(user_id):
    row = query("SELECT id,name,email,student_id,created_at FROM users WHERE id=%s",
                (user_id,), "one")
    return (jsonify(row), 200) if row else error_response("User not found", 404)

@app.post("/users")
def create_user():
    data = request.get_json(silent=True) or {}
    name, email = data.get("name", "").strip(), data.get("email", "").strip().lower()
    student_id, password = data.get("student_id", "").strip(), data.get("password", "")
    if not all([name, email, student_id, password]):
        return error_response("name, email, student_id and password are required")
    try:
        user_id = query(
            "INSERT INTO users(name,email,student_id,password_hash) VALUES(%s,%s,%s,%s)",
            (name, email, student_id, generate_password_hash(password)), "id", True)
        return jsonify({"id": user_id, "name": name, "email": email,
                        "student_id": student_id, "message": "User created"}), 201
    except Exception as exc:
        if "Duplicate" in str(exc):
            return error_response("An account with this email already exists", 409)
        return error_response(str(exc), 500)

@app.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email, password = data.get("email", "").strip().lower(), data.get("password", "")
    user = query("SELECT * FROM users WHERE email=%s", (email,), "one")
    if not user or not check_password_hash(user["password_hash"], password):
        return error_response("Invalid email or password", 401)
    return jsonify({"id": user["id"], "name": user["name"], "email": user["email"],
                    "student_id": user["student_id"], "message": "Login successful"})

@app.get("/")
def index():
    return jsonify({"service":"user-service","endpoints":["GET /users","POST /users","POST /login"]})

if __name__ == "__main__":
    app.run(port=5001, debug=True)
