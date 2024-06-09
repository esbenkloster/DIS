from datetime import datetime
from bank import conn, login_manager
from flask_login import UserMixin
from psycopg2 import sql

# Assuming you have a User class to represent users
class User(UserMixin):
    def __init__(self, id, username, email, role):
        self.id = id
        self.username = username
        self.email = email
        self.role = role

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    cur = conn.cursor()
    try:
        user_sql = """
        SELECT id, username, email, role FROM users WHERE id = %s
        """
        cur.execute(user_sql, (int(user_id),))
        user = cur.fetchone()
        if user:
            return User(user[0], user[1], user[2], user[3])
        return None
    except Exception as e:
        conn.rollback()  # Rollback the transaction if an error occurs
        print(f"Error loading user: {e}")
        return None
    finally:
        cur.close()  # Ensure the cursor is closed after the operation

def select_emp_policies(emp_id):
    cur = conn.cursor()
    try:
        sql_query = """
        SELECT p.policy_number, p.policy_type, p.start_date, p.end_date, p.premium_amount
        FROM policy p
        JOIN manages m ON p.id = m.policy_id
        JOIN employee e ON e.id = m.emp_id
        WHERE e.id = %s
        """
        cur.execute(sql_query, (emp_id,))
        tuple_resultset = cur.fetchall()
        return tuple_resultset
    except Exception as e:
        conn.rollback()
        print(f"Error selecting employee policies: {e}")
        return []
    finally:
        cur.close()

def select_emp_claims(emp_id):
    cur = conn.cursor()
    try:
        sql_query = """
        SELECT c.claim_date, c.description, c.amount, c.claim_status
        FROM claim c
        JOIN policy p ON p.id = c.policy_id
        JOIN manages m ON p.id = m.policy_id
        JOIN employee e ON e.id = m.emp_id
        WHERE e.id = %s
        """
        cur.execute(sql_query, (emp_id,))
        tuple_resultset = cur.fetchall()
        return tuple_resultset
    except Exception as e:
        conn.rollback()
        print(f"Error selecting employee claims: {e}")
        return []
    finally:
        cur.close()

def select_emp_payments(emp_id):
    cur = conn.cursor()
    try:
        sql_query = """
        SELECT py.payment_date, py.amount, py.payment_method
        FROM payment py
        JOIN policy p ON p.id = py.policy_id
        JOIN manages m ON p.id = m.policy_id
        JOIN employee e ON e.id = m.emp_id
        WHERE e.id = %s
        """
        cur.execute(sql_query, (emp_id,))
        tuple_resultset = cur.fetchall()
        return tuple_resultset
    except Exception as e:
        conn.rollback()
        print(f"Error selecting employee payments: {e}")
        return []
    finally:
        cur.close()
