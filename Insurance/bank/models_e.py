from datetime import datetime
from bank import conn, login_manager
from flask_login import UserMixin
from psycopg2 import sql

# @login_manager.user_loader
# def load_user(user_id):
#     # Implement loading of user based on user_id if needed
#     pass

def select_emp_policies(emp_id):
    """
    Query to retrieve policies managed by a specific employee.
    """
    cur = conn.cursor()
    sql = """
    SELECT p.policy_number, p.policy_type, p.start_date, p.end_date, p.premium_amount
    FROM policy p
    JOIN manages m ON p.id = m.policy_id
    JOIN employee e ON e.id = m.emp_id
    WHERE e.id = %s
    """
    cur.execute(sql, (emp_id,))
    tuple_resultset = cur.fetchall()
    cur.close()
    return tuple_resultset

def select_emp_claims(emp_id):
    """
    Query to retrieve claims managed by a specific employee.
    """
    cur = conn.cursor()
    sql = """
    SELECT c.claim_date, c.description, c.amount, c.claim_status
    FROM claim c
    JOIN policy p ON p.id = c.policy_id
    JOIN manages m ON p.id = m.policy_id
    JOIN employee e ON e.id = m.emp_id
    WHERE e.id = %s
    """
    cur.execute(sql, (emp_id,))
    tuple_resultset = cur.fetchall()
    cur.close()
    return tuple_resultset

def select_emp_payments(emp_id):
    """
    Query to retrieve payments managed by a specific employee.
    """
    cur = conn.cursor()
    sql = """
    SELECT py.payment_date, py.amount, py.payment_method
    FROM payment py
    JOIN policy p ON p.id = py.policy_id
    JOIN manages m ON p.id = m.policy_id
    JOIN employee e ON e.id = m.emp_id
    WHERE e.id = %s
    """
    cur.execute(sql, (emp_id,))
    tuple_resultset = cur.fetchall()
    cur.close()
    return tuple_resultset
