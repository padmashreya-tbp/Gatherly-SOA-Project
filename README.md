# Gatherly — Event Registration & Ticket Management (SOA)

A student project demonstrating Service-Oriented Architecture with five independent Flask REST services, a MySQL database, and a browser-based frontend.

## Architecture

| Service | Port | Main responsibility |
|---|---:|---|
| User Service | 5001 | Create accounts, list users, validate login |
| Event Service | 5002 | List/create/update events and reserve/release seats |
| Registration Service | 5003 | Validate users/events and coordinate registrations |
| Ticket Service | 5004 | Generate and look up unique ticket codes |
| Notification Service | 5005 | Store and display notifications |

The Registration Service calls the User, Event, Ticket, and Notification services through HTTP REST APIs. The services share the `gatherly_db` schema for this academic demonstration. A production deployment would normally consider stronger service isolation, authentication, retries, distributed transaction handling, and secrets management.

## Requirements

- Python 3.10 or newer
- MySQL Server 8.x running locally
- A modern browser

## Windows setup

1. Extract this project into a folder, for example `C:\Users\<your-user>\Desktop\Gatherly_SOA_Project`.
2. Open PowerShell in that folder.
3. Create a virtual environment and install dependencies:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and put your local MySQL password in `DB_PASSWORD`. Keep `.env` private.
5. Open MySQL Workbench, open `schema.sql`, and execute the full script. It creates `gatherly_db`, its tables, and three sample events.
6. Start all five services:

   ```powershell
   python run_services.py
   ```

7. Open `frontend\index.html` in your browser. If the browser blocks local-file requests, serve the frontend from a second PowerShell window:

   ```powershell
   cd frontend
   py -m http.server 8000
   ```

   Then visit `http://127.0.0.1:8000`.

8. Check that each service is healthy:
   - `http://127.0.0.1:5001/health`
   - `http://127.0.0.1:5002/health`
   - `http://127.0.0.1:5003/health`
   - `http://127.0.0.1:5004/health`
   - `http://127.0.0.1:5005/health`

## Main demonstration flow

1. Create an account in the frontend.
2. Note the user ID displayed after successful creation.
3. Choose an event and register.
4. The Registration Service validates the user and event via REST calls, reserves a seat, creates a registration, asks Ticket Service for a ticket, and asks Notification Service to store a confirmation.
5. Use the ticket code to look up the ticket.
6. Enter the user ID in Notifications to see the confirmation.

## Useful API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/users` | List users |
| POST | `/users` | Create user |
| POST | `/login` | Check email/password |
| GET | `/events` | List events |
| POST | `/events` | Create event |
| PUT | `/events/<id>` | Update event details |
| POST | `/events/<id>/reserve` | Reserve one seat |
| POST | `/events/<id>/release` | Release one seat |
| GET | `/registrations` | List registrations |
| POST | `/registrations` | Register a user for an event |
| POST | `/registrations/<id>/cancel` | Cancel registration |
| GET | `/tickets` | List tickets |
| GET | `/tickets/<ticket_code>` | Look up a ticket |
| POST | `/tickets` | Generate a ticket for a confirmed registration |
| GET | `/notifications?user_id=<id>` | List a user's notifications |
| POST | `/notifications` | Create a notification |

POST requests accept JSON. Example create-user request:

```json
{
  "name": "Sample Student",
  "email": "student@example.com",
  "student_id": "STU001",
  "password": "change-this-password"
}
```

Example event request:

```json
{
  "name": "Cloud Computing Workshop",
  "description": "A practical introduction to cloud platforms.",
  "event_date": "2027-02-10 10:00:00",
  "venue": "Seminar Hall",
  "capacity": 60
}
```

## Suggested submission checklist

- [ ] Add your name, roll number, course, faculty name, and date to a cover page/report if required.
- [ ] Run the app locally and capture screenshots of the events list, account creation, successful registration, ticket lookup, and notifications.
- [ ] Test one invalid user ID and one event with no available seats.
- [ ] Read the architecture section and be ready to explain how REST calls connect the services.
- [ ] Do not include `.env`, passwords, or local database files in a public GitHub repository.

## Limitations / future enhancements

This is an academic demonstration, not a production ticketing platform. Login is provided as an API endpoint but the demo UI uses the created user ID rather than maintaining a secure session. Email/SMS delivery, role-based access, payment processing, automated reminders, and robust distributed rollback/retry handling are not implemented. Add and test any features required by your course rubric before submission.
