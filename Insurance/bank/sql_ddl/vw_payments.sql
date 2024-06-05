CREATE OR REPLACE VIEW vw_payments AS
SELECT 
    p.policy_number,
    p.payment_date,
    p.amount,
    p.payment_method
FROM 
    Payments p
JOIN 
    Policies po ON p.policy_number = po.policy_number;
