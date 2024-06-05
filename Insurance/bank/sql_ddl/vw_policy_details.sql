CREATE OR REPLACE VIEW vw_policy_details AS
SELECT 
    p.policy_number,
    p.policy_type,
    p.start_date,
    p.end_date,
    p.premium_amount,
    c.name AS customer_name,
    c.address AS customer_address,
    c.phone_number AS customer_phone,
    c.email AS customer_email
FROM 
    Policies p
JOIN 
    Customers c ON p.CPR_number = c.CPR_number;
