from datetime import datetime
from bank import conn, login_manager
from flask_login import UserMixin
from psycopg2 import sql

@login_manager.user_loader
def load_user(user_id):
    cur = conn.cursor()

    schema = 'customers'
    id = 'cpr_number'
    if str(user_id).startswith('60'):
        schema = 'employees'
        id = 'id'

    user_sql = sql.SQL("""
    SELECT * FROM {}
    WHERE {} = %s
    """).format(sql.Identifier(schema),  sql.Identifier(id))

    cur.execute(user_sql, (int(user_id),))
    if cur.rowcount > 0:
        return Employees(cur.fetchone()) if schema == 'employees' else Customers(cur.fetchone())
    else:
        return None

class Customers(tuple, UserMixin):
    def __init__(self, user_data):
        self.CPR_number = user_data[0]
        self.policy_number = user_data[1]
        self.password = user_data[2]
        self.name = user_data[3]
        self.address = user_data[4]
        self.phone_number = user_data[5]
        self.email = user_data[6]
        self.role = "customer"

    def get_id(self):
        return self.CPR_number

class Employees(tuple, UserMixin):
    def __init__(self, employee_data):
        self.id = employee_data[0]
        self.name = employee_data[1]
        self.password = employee_data[2]
        self.department = employee_data[3]
        self.role = "employee"

    def get_id(self):
        return self.id

class Policy(tuple):
    def __init__(self, policy_data):
        self.policy_number = policy_data[0]
        self.policy_type = policy_data[1]
        self.start_date = policy_data[2]
        self.end_date = policy_data[3]
        self.premium_amount = policy_data[4]
        self.CPR_number = policy_data[5]

class Claim(tuple):
    def __init__(self, claim_data):
        self.claim_id = claim_data[0]
        self.policy_number = claim_data[1]
        self.claim_date = claim_data[2]
        self.amount = claim_data[3]
        self.status = claim_data[4]
        self.description = claim_data[5]

def insert_Customer(name, CPR_number, password, address, ):
    cur = conn.cursor()
    sql = """
    INSERT INTO customers (name, CPR_number, password)
    VALUES (%s, %s, %s)
    """
    cur.execute(sql, (name, CPR_number, password))
    conn.commit()
    cur.close()

def select_Customer(CPR_number):
    cur = conn.cursor()
    sql = """
    SELECT * FROM customers
    WHERE CPR_number = %s
    """
    cur.execute(sql, (CPR_number,))
    user = Customers(cur.fetchone()) if cur.rowcount > 0 else None
    cur.close()
    return user

def select_customer_direct(CPR_number):
    cur = conn.cursor()
    sql = """
    SELECT * FROM customers
    WHERE CPR_number = %s
    AND direct IS TRUE
    """
    cur.execute(sql, (CPR_number,))
    user = Customers(cur.fetchone()) if cur.rowcount > 0 else None
    cur.close()
    return user

def select_customers_direct():
    cur = conn.cursor()
    sql = """
    SELECT
      c.name customer
    , cpr_number
    , address
    FROM customers c
	WHERE direct IS TRUE
    ;
    """
    cur.execute(sql)
    tuple_resultset = cur.fetchall()
    cur.close()
    return tuple_resultset

def select_Employee(id):
    cur = conn.cursor()
    sql = """
    SELECT * FROM employees
    WHERE id = %s
    """
    cur.execute(sql, (id,))
    user = Employees(cur.fetchone()) if cur.rowcount > 0 else None
    cur.close()
    return user

def insert_Policy(CPR_number, policy_type, premium, coverage, created_date=datetime.now()):
    cur = conn.cursor()
    sql = """
    INSERT INTO policies (CPR_number, policy_type, premium, coverage, created_date)
    VALUES (%s, %s, %s, %s, %s)
    """
    cur.execute(sql, (CPR_number, policy_type, premium, coverage, created_date))
    conn.commit()
    cur.close()

def select_Customer_Policies(CPR_number):
    cur = conn.cursor()
    sql = """
    SELECT * FROM policies
    WHERE CPR_number = %s
    """
    cur.execute(sql, (CPR_number,))
    policies = [Policy(row) for row in cur.fetchall()]
    cur.close()
    return policies

def insert_Claim(policy_number, claim_date, amount, status='Pending'):
    cur = conn.cursor()
    sql = """
    INSERT INTO claims (policy_number, claim_date, amount, status)
    VALUES (%s, %s, %s, %s)
    """
    cur.execute(sql, (policy_number, claim_date, amount, status))
    conn.commit()
    cur.close()

def select_Policy_Claims(policy_number):
    cur = conn.cursor()
    sql = """
    SELECT * FROM claims
    WHERE policy_number = %s
    """
    cur.execute(sql, (policy_number,))
    claims = [Claim(row) for row in cur.fetchall()]
    cur.close()
    return claims

def update_Claim_Status(claim_number, status):
    cur = conn.cursor()
    sql = """
    UPDATE claims
    SET status = %s
    WHERE claim_number = %s
    """
    cur.execute(sql, (status, claim_number))
    conn.commit()
    cur.close()

def select_cus_accounts(cpr_number):
    cur = conn.cursor()
    sql = """
    SELECT
      e.name employee
    , c.name customer
    , cpr_number
    , account_number
    FROM manages m
      NATURAL JOIN accounts
      NATURAL JOIN customers c
      LEFT OUTER JOIN employees e ON m.emp_cpr_number = e.id
	WHERE cpr_number = %s
    ;
    """
    cur.execute(sql, (cpr_number,))
    tuple_resultset = cur.fetchall()
    cur.close()
    return tuple_resultset
