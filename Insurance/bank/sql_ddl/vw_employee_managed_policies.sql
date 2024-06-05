CREATE OR REPLACE VIEW vw_employee_managed_policies AS
SELECT 
    e.name AS employee_name,
    e.department,
    p.policy_number,
    p.policy_type,
    p.start_date,
    p.end_date,
    p.premium_amount
FROM 
    Manages m
JOIN 
    Employees e ON m.emp_id = e.id
JOIN 
    Policies p ON m.policy_number = p.policy_number;