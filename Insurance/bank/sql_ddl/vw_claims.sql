CREATE OR REPLACE VIEW vw_claims AS
SELECT 
    c.policy_number,
    c.claim_date,
    c.claim_amount,
    c.claim_status,
    c.description
FROM 
    Claims c
JOIN 
    Policies p ON c.policy_number = p.policy_number;
