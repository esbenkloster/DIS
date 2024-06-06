--
-- schema_ins.sql
-- Populate bank schema with data.
--
\echo Emptying the bank database. Deleting all tuples.
--
-- Dependency level 2
-- Referential integrity to level 1 and 0
--
DELETE FROM manages;
DELETE FROM payments;
DELETE FROM claims;
--
-- Dependency level 1
-- Referential integrity to level 0
--
DELETE FROM policies;
--
-- Dependency level 0. 
-- No referential integrity constraints
--
DELETE FROM employees;
DELETE FROM customers;

-- Insertion file for Insurance Web Application

\echo .
\echo
\echo Adding data to Customers:
INSERT INTO Customers (CPR_number, policy_number, password, name, address, phone_number, email) VALUES
(1001, 'P123456', 'password123', 'John Doe', '123 Elm St', '+1 555 1234567', 'john.doe@example.com'),
(1002, 'P123457', 'password456', 'Jane Smith', '456 Oak St', '+1 555 2345678', 'jane.smith@example.com'),
-- wrong email format to check the regex constraint
(1003, 'P123458', 'password789', 'Alice Johnson', '789 Pine St', '+1 555 3456789', 'alice.johnson.com');
(1004, 'P123459', 'password321', 'Sam Ericsen', '325 Asp St', '+1 555 9876543', 'sam.ericsen@example.com');

\echo .
\echo Adding data to Employees:
INSERT INTO Employees (id, name, password, department) VALUES
(601, 'Robert Brown', 'admin123', 'Claims'),
(602, 'Emily Davis', 'admin456', 'Underwriting'),
(603, 'Michael Wilson', 'admin789', 'Customer Service');

\echo .
\echo Adding data to Policies:
INSERT INTO Policies (policy_number, policy_type, start_date, end_date, premium_amount, CPR_number) VALUES
('P123456', 'Health Insurance', '2023-01-01', '2024-01-01', 1200.00, 1001),
('P123457', 'Auto Insurance', '2023-02-01', '2024-02-01', 900.00, 1002),
-- trying to add a policy with a non-existing customer (to check if the customer correctly was not added to the database)
('P123458', 'Home Insurance', '2023-03-01', '2024-03-01', 1500.00, 1003);

\echo .
\echo Adding data to Claims:
INSERT INTO Claims (policy_number, claim_date, claim_amount, claim_status, description) VALUES
('P123456', '2023-05-15', 300.00, 'Approved', 'Medical expenses'),
('P123457', '2023-06-20', 500.00, 'Pending', 'Car accident repair'),
('P123459', '2023-07-10', 700.00, 'Denied', 'Roof damage from storm');

\echo .
\echo Adding data to Payments:
INSERT INTO Payments (policy_number, payment_date, amount, payment_method) VALUES
('P123456', '2023-01-01', 1200.00, 'Credit Card'),
('P123457', '2023-02-01', 900.00, 'Bank Transfer'),
('P123459', '2023-03-01', 1500.00, 'Credit Card');

\echo .
\echo Adding data to Manages:
INSERT INTO Manages (emp_id, policy_number) VALUES
(1, 'P123456'),
(2, 'P123457'),
(3, 'P123459');

\echo ...............
\echo done
