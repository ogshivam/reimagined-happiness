
-- Sample PostgreSQL Database Script
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10,2),
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255) UNIQUE,
    city VARCHAR(100),
    country VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(id),
    product_id INT REFERENCES products(id),
    quantity INT,
    order_date DATE
);

-- Sample data
INSERT INTO products (name, price, category) VALUES
('Laptop', 999.99, 'Electronics'),
('Mouse', 29.99, 'Electronics'),
('Coffee Mug', 12.50, 'Kitchen'),
('Book', 19.99, 'Books'),
('Phone', 699.99, 'Electronics');

INSERT INTO customers (first_name, last_name, email, city, country) VALUES
('John', 'Doe', 'john@example.com', 'New York', 'USA'),
('Jane', 'Smith', 'jane@example.com', 'London', 'UK'),
('Bob', 'Johnson', 'bob@example.com', 'Toronto', 'Canada');

INSERT INTO orders (customer_id, product_id, quantity, order_date) VALUES
(1, 1, 1, '2024-01-15'),
(2, 2, 2, '2024-01-16'),
(3, 3, 1, '2024-01-17');
