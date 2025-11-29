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

-- Comments table Technicians and Requesters add comments to tickets
CREATE TABLE comments (
    comment_id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id INT NOT NULL,
    user_id INT NOT NULL,
    comment_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    
    INDEX idx_comments_ticket_id (ticket_id),
    INDEX idx_comments_user_id (user_id)
);


-- Ratings table Requester rates resolved tickets
CREATE TABLE ratings (
    rating_id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id INT NOT NULL UNIQUE, 
    rating_value INT NOT NULL CHECK (rating_value BETWEEN 1 AND 5),
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id) ON DELETE CASCADE,
    
    INDEX idx_ratings_ticket_id (ticket_id)
);

-- Report log table Managers generate reports
CREATE TABLE report_logs (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    manager_id INT NOT NULL,
    report_type VARCHAR(50) NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (manager_id) REFERENCES users(user_id),
    
    INDEX idx_report_logs_manager_id (manager_id),
    INDEX idx_report_logs_generated_at (generated_at)
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