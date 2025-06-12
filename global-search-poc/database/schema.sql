-- ORDERS table
CREATE TABLE orders (
    order_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20),
    order_date DATE,
    amount NUMERIC(10, 2),
    status VARCHAR(20)
);

-- CHANGE_LOG table (for delta refresh simulation)
CREATE TABLE change_log (
    id IDENTITY PRIMARY KEY,
    table_name VARCHAR(50),
    record_id VARCHAR(20),
    change_type VARCHAR(10),
    change_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- This file is your database initializer.
-- You run this once in your H2 console to set up your mock DB.
