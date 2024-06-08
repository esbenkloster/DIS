from datetime import datetime
from bank import conn, login_manager
from flask_login import UserMixin
from psycopg2 import sql, Error

@login_manager.user_loader
def load_user(user_id):
    try:
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
            user_data = cur.fetchone()
            cur.close()
            return Employees(user_data) if schema == 'employees' else Customers(user_data)
        else:
            cur.close()
            return None
    except Error as e:
        print(f"Database error: {e}")
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
        self.balance = user_data[7]
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

class Policy:
    def __init__(self, policy_data):
        if len(policy_data) == 6:
            self.policy_number = policy_data[0]
            self.policy_type = policy_data[1]
            self.start_date = policy_data[2]
            self.end_date = policy_data[3]
            self.premium_amount = policy_data[4]
            self.CPR_number = policy_data[5]
        elif len(policy_data) == 2:
            self.policy_type = policy_data[0]
            self.premium_amount = policy_data[1]
        else:
            raise ValueError("Invalid policy data")

class Claim(tuple):
    def __init__(self, claim_data):
        self.claim_id = claim_data[0]
        self.policy_number = claim_data[1]
        self.claim_date = claim_data[2]
        self.amount = claim_data[3]
        self.status = claim_data[4]
        self.description = claim_data[5]

class Payment(tuple):
    def __init__(self, payment_data):
        self.payment_id = payment_data[0]
        self.policy_number = payment_data[1]
        self.payment_date = payment_data[2]
        self.amount = payment_data[3]
        self.payment_method = payment_data[4]

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
    SELECT policy_number, policy_type, start_date, end_date, premium_amount, CPR_number
    FROM policies
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

def select_Policy_Claims(policy_number=None):
    cur = conn.cursor()
    if policy_number:
        sql = """
        SELECT * FROM claims
        WHERE policy_number = %s
        """
        cur.execute(sql, (policy_number,))
    else:
        sql = """
        SELECT * FROM claims
        """
        cur.execute(sql)
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
    try:
        cur = conn.cursor()
        account_sql = """
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
        cur.execute(account_sql, (cpr_number,))
        accounts = cur.fetchall()
        cur.close()
        return accounts
    except Error as e:
        print(f"Database error: {e}")
        return []

def select_Policy_Payments(policy_number):
    cur = conn.cursor()
    sql = """
    SELECT * FROM payments
    WHERE policy_number = %s
    """
    cur.execute(sql, (policy_number,))
    payments = [Payment(row) for row in cur.fetchall()]
    cur.close()
    return payments

class Policy:
    def __init__(self, policy_data):
        self.policy_number = policy_data[0]
        self.policy_type = policy_data[1]
        self.start_date = policy_data[2]
        self.end_date = policy_data[3]
        self.premium_amount = policy_data[4]
        self.CPR_number = policy_data[5]

def select_All_Policy_Types():
    cur = conn.cursor()
    sql = """
    SELECT DISTINCT policy_type, premium_amount
    FROM Policies
    """
    cur.execute(sql)
    policies = [Policy(row) for row in cur.fetchall()]
    cur.close()
    return policies

def select_Policy_Details_By_Type(policy_type):
    cur = conn.cursor()
    sql = """
    SELECT policy_type, premium_amount
    FROM Policies
    WHERE policy_type = %s
    LIMIT 1
    """
    cur.execute(sql, (policy_type,))
    policy = Policy(cur.fetchone())
    cur.close()
    return policy

def select_available_policies(CPR_number):
    cur = conn.cursor()
    sql = """
    SELECT DISTINCT policy_type, premium_amount
    FROM policies
    WHERE CPR_number != %s
    AND policy_type NOT IN (
        SELECT policy_type
        FROM policies
        WHERE CPR_number = %s
    )
    """
    cur.execute(sql, (CPR_number, CPR_number))
    available_policies = [row for row in cur.fetchall()]
    cur.close()
    return available_policies
