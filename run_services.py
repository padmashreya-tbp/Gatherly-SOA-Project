
import subprocess
import sys
import time
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent

SERVICES = [
    ("user-service", ROOT / "user_service" / "app.py"),
    ("event-service", ROOT / "event_service" / "app.py"),
    ("registration-service", ROOT / "registration_service" / "app.py"),
    ("ticket-service", ROOT / "ticket_service" / "app.py"),
    ("notification-service", ROOT / "notification_service" / "app.py"),
]

processes = []

env = os.environ.copy()
env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")

try:
    for name, script in SERVICES:
        print(f"Starting {name}: {script}", flush=True)
        processes.append(
            subprocess.Popen(
                [sys.executable, str(script)],
                cwd=str(ROOT),
                env=env
            )
        )
        time.sleep(0.7)

    print("\nAll services launched. Open frontend/index.html in your browser.", flush=True)
    print("Press Ctrl+C to stop all services.", flush=True)

    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\nStopping services...", flush=True)

finally:
    for p in processes:
        p.terminate()

    for p in processes:
        try:
            p.wait(timeout=3)
        except subprocess.TimeoutExpired:
            p.kill()
