-- Campus Ticket Management System 

-- Users table (for authentication)
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('requester', 'technician', 'manager') NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Categories table
CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    description TEXT
);

-- Ticket status table
CREATE TABLE ticket_status (
    status_id INT AUTO_INCREMENT PRIMARY KEY,
    status_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

-- Tickets table (main table)
CREATE TABLE tickets (
    ticket_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(255) NOT NULL,
    category_id INT,
    status_id INT DEFAULT 1,
    requester_id INT,
    technician_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (status_id) REFERENCES ticket_status(status_id),
    FOREIGN KEY (requester_id) REFERENCES users(user_id),
    FOREIGN KEY (technician_id) REFERENCES users(user_id)
);

-- Indexes
CREATE INDEX idx_email ON users(email);
CREATE INDEX idx_role ON users(role);
CREATE INDEX idx_requester_id ON tickets(requester_id);
CREATE INDEX idx_technician_id ON tickets(technician_id);
CREATE INDEX idx_status_id ON tickets(status_id);
CREATE INDEX idx_category_id ON tickets(category_id);

-- Default data
INSERT INTO ticket_status (status_name, description) VALUES
('Pending', 'Ticket submitted but not yet assigned'),
('In Progress', 'Ticket assigned and being worked on'),
('Resolved', 'Ticket has been completed'),
('Closed', 'Ticket is finalized');

INSERT INTO categories (category_name, description) VALUES
('IT Support', 'Computer, network, and software issues'),
('Facilities', 'Building maintenance, repairs, and cleaning'),
('Electrical', 'Power outlets, lighting, electrical systems'),
('Plumbing', 'Leaks, clogs, water-related issues'),
('HVAC', 'Heating, ventilation, and air conditioning');