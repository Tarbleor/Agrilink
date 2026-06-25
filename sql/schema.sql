DROP DATABASE IF EXISTS agrilink_sl;
CREATE DATABASE agrilink_sl;
USE agrilink_sl;

CREATE TABLE users (
 id INT AUTO_INCREMENT PRIMARY KEY,
 full_name VARCHAR(120) NOT NULL,
 email VARCHAR(120) NOT NULL UNIQUE,
 phone VARCHAR(30) NOT NULL UNIQUE,
 district VARCHAR(80) NOT NULL,
 password_hash VARCHAR(255) NOT NULL,
 role ENUM('admin','farmer') NOT NULL DEFAULT 'farmer',
 is_active TINYINT(1) NOT NULL DEFAULT 1,
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE crops (
 id INT AUTO_INCREMENT PRIMARY KEY,
 name VARCHAR(100) NOT NULL UNIQUE,
 crop_type VARCHAR(80) NOT NULL,
 description TEXT,
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE markets (
 id INT AUTO_INCREMENT PRIMARY KEY,
 name VARCHAR(120) NOT NULL,
 district VARCHAR(80) NOT NULL,
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE prices (
 id INT AUTO_INCREMENT PRIMARY KEY,
 crop_id INT NOT NULL,
 market_id INT NOT NULL,
 price DECIMAL(10,2) NOT NULL,
 unit VARCHAR(30) NOT NULL DEFAULT 'kg',
 note VARCHAR(255),
 updated_by INT,
 updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY (crop_id) REFERENCES crops(id) ON DELETE CASCADE,
 FOREIGN KEY (market_id) REFERENCES markets(id) ON DELETE CASCADE,
 FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL
);

INSERT INTO users(full_name,email,phone,district,password_hash,role,is_active) VALUES
('System Administrator','admin@agrilink.sl','+232000000001','Freetown','admin123','admin',1),
('Demo Farmer','farmer@agrilink.sl','+232000000002','Bo','farmer123','farmer',1);

INSERT INTO crops(name,crop_type,description) VALUES
('Rice','Cereal','A staple food crop commonly traded across Sierra Leone.'),
('Cassava','Root Crop','A major food crop used for garri, foofoo, and local consumption.'),
('Palm Oil','Oil Crop','A high-demand agricultural product used for cooking and trading.'),
('Groundnut','Legume','A valuable crop sold in local and urban markets.'),
('Pepper','Vegetable','A common vegetable crop with frequent price changes.');

INSERT INTO markets(name,district) VALUES
('Dove Cut Market','Freetown'),
('Bo Central Market','Bo'),
('Kenema Main Market','Kenema'),
('Makeni Market','Bombali'),
('Koidu Market','Kono');

INSERT INTO prices(crop_id,market_id,price,unit,note,updated_by) VALUES
(1,1,650.00,'bag','High demand in urban market',1),
(1,2,620.00,'bag','Stable supply',1),
(2,2,35.00,'bundle','Fresh harvest supply',1),
(2,3,38.00,'bundle','Transport cost added',1),
(3,3,780.00,'gallon','Strong regional demand',1),
(3,1,820.00,'gallon','Higher city price',1),
(4,4,420.00,'bag','Moderate supply',1),
(5,5,28.00,'cup','Seasonal price rise',1);
