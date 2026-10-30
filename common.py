import os
from functools import wraps
from flask import jsonify
import mysql.connector
from mysql.connector import pooling
from dotenv import load_dotenv

load_dotenv()
_pool = None

def get_pool():
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name="gatherly_pool",
            pool_size=10,
            host=os.getenv("DB_HOST", "127.0.0.1"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "gatherly_db"),
            autocommit=False,
        )
    return _pool

def query(sql, params=(), fetch="all", commit=False):
    conn = get_pool().get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(sql, params)
        result = None
        if fetch == "one":
            result = cur.fetchone()
        elif fetch == "all":
            result = cur.fetchall()
        elif fetch == "id":
            result = cur.lastrowid
        if commit:
            conn.commit()
        return result
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def service_app(name):
    from flask import Flask
    from flask_cors import CORS
    app = Flask(name)
    CORS(app)
    app.config["JSON_SORT_KEYS"] = False

    @app.get("/health")
    def health():
        try:
            query("SELECT 1", fetch="one")
            return jsonify({"service": name, "status": "ok", "database": "connected"})
        except Exception as exc:
            return jsonify({"service": name, "status": "error", "error": str(exc)}), 503
    return app

def error_response(message, status=400):
    return jsonify({"error": message}), status
