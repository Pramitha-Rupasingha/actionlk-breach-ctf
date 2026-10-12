CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'employee'
);

-- Intentionally weak/plaintext for the CTF scenario — this is seed data for
-- an isolated training box, never for a real credential store.
INSERT INTO users (username, password, role) VALUES
    ('k.perera', 'Summer2025!', 'employee'),
    ('admin', 'R00t_P0rtal_9x2', 'admin');
