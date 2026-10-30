# GATHERLY
## Event Registration and Ticket Management System
### Service-Oriented Architecture — Project Report

**Student Name:** ____________________  
**Roll Number:** ____________________  
**Course:** Service-Oriented Architecture  
**Faculty:** ____________________  
**Institution:** ____________________  
**Academic Year:** ____________________

## 1. Abstract
Gatherly is an event registration and ticket management application developed to demonstrate Service-Oriented Architecture. It separates user management, event management, registration, ticket generation, and notifications into independent REST services. The frontend communicates with the services through HTTP APIs, and MySQL stores the application's records.

## 2. Problem Statement
Managing campus events manually can make it difficult to maintain attendee lists, track seat availability, issue tickets, and send registration confirmations. Gatherly provides a central interface for these tasks while separating business capabilities into services.

## 3. Objectives
- Build independent services for users, events, registrations, tickets, and notifications.
- Expose functionality through REST endpoints using JSON.
- Store application records in MySQL.
- Validate users and events before registration.
- Track seat availability and prevent reservations when an event is full.
- Generate unique ticket codes and store confirmation notifications.

## 4. Technology Stack
- Frontend: HTML, CSS, JavaScript
- Backend: Python and Flask
- Communication: REST APIs over HTTP using JSON
- Database: MySQL
- Testing: Browser and API requests (Postman may also be used)
- Development: Visual Studio Code / PowerShell / MySQL Workbench

## 5. Architecture
The system contains five services:
1. User Service — creates and retrieves user records and checks login credentials.
2. Event Service — lists and maintains events and manages seat inventory.
3. Registration Service — coordinates the registration workflow.
4. Ticket Service — generates unique ticket codes and provides ticket lookup.
5. Notification Service — records registration notifications and supports user-specific retrieval.

The browser frontend calls REST endpoints. The Registration Service calls other services over HTTP, which demonstrates service composition and loose coupling at the API level. The services share one MySQL schema in this teaching version to simplify setup.

## 6. Database Design
- `users`: user identity, email, student ID, password hash, creation timestamp.
- `events`: event details, date, venue, capacity, available seats.
- `registrations`: user/event relationship, registration date, status.
- `tickets`: unique ticket code, related registration, status.
- `notifications`: recipient, message, type, read status, timestamp.

Foreign keys maintain relationships between registrations, users, events, tickets, and notifications. A unique constraint prevents the same user from having duplicate registration rows for one event.

## 7. Registration Workflow
1. The user selects an event and submits their user ID.
2. Registration Service calls User Service and Event Service to validate the records.
3. The event's available-seat count is checked.
4. A registration is created and the Event Service atomically reserves a seat.
5. Ticket Service creates a unique ticket code for the confirmed registration.
6. Notification Service stores a confirmation message.
7. The frontend displays the registration result and ticket code.

## 8. Testing Plan
Record the actual result after running each test.

| Test case | Expected result | Actual result |
|---|---|---|
| Open events page | Sample events are displayed | __________ |
| Create account with valid details | User ID is returned | __________ |
| Create account with duplicate email | Clear error message | __________ |
| Register for an available event | Registration and ticket code returned | __________ |
| Register twice for the same event | Duplicate registration rejected | __________ |
| Look up valid ticket code | Ticket and event details displayed | __________ |
| Look up invalid ticket code | Not-found message displayed | __________ |
| Load notifications by user ID | Saved notifications displayed | __________ |
| Health endpoint with database running | Service reports healthy | __________ |

## 9. Advantages
- Each business capability has a separate service.
- Services expose clear REST endpoints.
- JSON makes service communication language-independent.
- Services can be developed and tested independently.
- Ticket and notification records are managed separately from event listings.

## 10. Limitations
This demonstration shares one database schema among services and does not implement a full distributed transaction protocol. It does not include payment processing, external email/SMS delivery, role-based authorization, or production-grade session management. A real deployment would require additional security, monitoring, retries, and failure recovery.

## 11. Future Scope
- Add organizer/admin roles and secure sessions.
- Add QR-code tickets and ticket scanning.
- Send email or SMS confirmations and reminders.
- Add payment integration where appropriate.
- Add service discovery, an API gateway, containers, and monitoring.
- Use a message broker for asynchronous notification processing.

## 12. Conclusion
Gatherly demonstrates the core SOA idea of organizing an application into services that expose reusable APIs. The registration workflow coordinates user validation, event seat reservation, ticket generation, and notification creation to provide an end-to-end event booking demonstration.
