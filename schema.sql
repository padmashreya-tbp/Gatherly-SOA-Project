CREATE DATABASE IF NOT EXISTS gatherly_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE gatherly_db;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  student_id VARCHAR(50) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS events (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  description TEXT,
  event_date DATETIME NOT NULL,
  venue VARCHAR(200) NOT NULL,
  capacity INT NOT NULL DEFAULT 50,
  available_seats INT NOT NULL DEFAULT 50,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS registrations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  event_id INT NOT NULL,
  registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  status ENUM('confirmed','cancelled') NOT NULL DEFAULT 'confirmed',
  UNIQUE KEY unique_user_event (user_id, event_id),
  CONSTRAINT fk_registration_user FOREIGN KEY (user_id) REFERENCES users(id),
  CONSTRAINT fk_registration_event FOREIGN KEY (event_id) REFERENCES events(id)
);

CREATE TABLE IF NOT EXISTS tickets (
  id INT AUTO_INCREMENT PRIMARY KEY,
  ticket_id VARCHAR(40) NOT NULL UNIQUE,
  registration_id INT NOT NULL UNIQUE,
  status ENUM('valid','cancelled') NOT NULL DEFAULT 'valid',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_ticket_registration FOREIGN KEY (registration_id) REFERENCES registrations(id)
);

CREATE TABLE IF NOT EXISTS notifications (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  message VARCHAR(500) NOT NULL,
  notification_type VARCHAR(50) NOT NULL DEFAULT 'registration',
  is_read BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_notification_user FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Optional demo data. Passwords are demo-only and stored as Werkzeug hashes
-- by the application when users are created. Create users from the UI/API.
INSERT INTO events (name, description, event_date, venue, capacity, available_seats)
SELECT 'Tech Innovation Summit', 'Talks and demonstrations on emerging technology.',
       DATE_ADD(NOW(), INTERVAL 14 DAY), 'Main Auditorium', 100, 100
WHERE NOT EXISTS (SELECT 1 FROM events WHERE name='Tech Innovation Summit');

INSERT INTO events (name, description, event_date, venue, capacity, available_seats)
SELECT 'Campus Cultural Fest', 'A celebration of music, dance, art and culture.',
       DATE_ADD(NOW(), INTERVAL 21 DAY), 'College Open Grounds', 250, 250
WHERE NOT EXISTS (SELECT 1 FROM events WHERE name='Campus Cultural Fest');

INSERT INTO events (name, description, event_date, venue, capacity, available_seats)
SELECT 'AI and Data Science Workshop', 'Hands-on introduction to AI and data science.',
       DATE_ADD(NOW(), INTERVAL 30 DAY), 'Computer Science Lab', 40, 40
WHERE NOT EXISTS (SELECT 1 FROM events WHERE name='AI and Data Science Workshop');
