\i schema_drop.sql

CREATE TABLE IF NOT EXISTS Customers(
    CPR_number integer PRIMARY KEY,
    policy_number varchar(20) UNIQUE,
    password varchar(120),
    name varchar(60),
    address text,
    phone_number varchar(15),
    email varchar(100)
    CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

CREATE TABLE IF NOT EXISTS Employees(
    id integer PRIMARY KEY,
    name varchar(60),
    password varchar(120),
    department varchar(50)
);

CREATE TABLE IF NOT EXISTS Policies(
    policy_number varchar(20) PRIMARY KEY,
    policy_type varchar(50),
    start_date date,
    end_date date,
    premium_amount decimal(10, 2),
    CPR_number integer REFERENCES Customers(CPR_number)
);

CREATE TABLE IF NOT EXISTS Claims(
    claim_id SERIAL PRIMARY KEY,
    policy_number varchar(20) REFERENCES Policies(policy_number),
    claim_date date,
    claim_amount decimal(10, 2),
    claim_status varchar(20),
    description text
);

CREATE TABLE IF NOT EXISTS Payments(
    payment_id SERIAL PRIMARY KEY,
    policy_number varchar(20) REFERENCES Policies(policy_number),
    payment_date date,
    amount decimal(10, 2),
    payment_method varchar(30)
);

CREATE TABLE IF NOT EXISTS Manages(
    emp_id INTEGER NOT NULL REFERENCES Employees(id),
    policy_number varchar(20) NOT NULL REFERENCES Policies(policy_number)
);
-- ALTER TABLE Manages ADD CONSTRAINT pk_manages PRIMARY KEY (emp_id, policy_number);

-- -- Adding a regex constraint to ensure phone number follows a pattern
-- ALTER TABLE Customers ADD CONSTRAINT phone_number_format CHECK (phone_number ~ '^\+\d{1,3}\s?\d{4,14}$');


-- CREATE TRIGGER email_check BEFORE INSERT ON Customers
-- FOR EACH ROW
-- BEGIN
--     IF NEW.email NOT REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$' THEN
--         SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid email format';
--     END IF;
-- END;
