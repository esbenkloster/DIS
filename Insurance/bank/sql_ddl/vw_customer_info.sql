CREATE OR REPLACE VIEW vw_customer_info AS
SELECT 
    CPR_number,
    name,
    address,
    phone_number,
    email
FROM 
    Customers;