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
        self.description = claim_data[2]
        self.amount = claim_data[3]
        self.claim_date = claim_data[4]
        self.status = claim_data[5]
        
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

def select_cus_claims(cpr_number):
    cur = conn.cursor()
    
    # Fetch the policies associated with the customer
    sql_policies = """
    SELECT policy_number FROM policies
    WHERE CPR_number = %s
    """
    cur.execute(sql_policies, (cpr_number,))
    policy_numbers = [row[0] for row in cur.fetchall()]
    
    # If no policies are found, return an empty list
    if not policy_numbers:
        cur.close()
        return []

    # Fetch the claims associated with the policy numbers
    sql_claims = """
    SELECT * FROM claims
    WHERE policy_number = ANY(%s)
    """
    cur.execute(sql_claims, (policy_numbers,))
    claims = [Claim(row) for row in cur.fetchall()]
    
    cur.close()
    return claims


def insert_Claim(policy_number, claim_date, claim_amount, claim_status='Pending'):
    cur = conn.cursor()
    sql = """
    INSERT INTO claims (policy_number, claim_date, claim_amount, claim_status)
    VALUES (%s, %s, %s, %s)
    """
    cur.execute(sql, (policy_number, claim_date, claim_amount, claim_status))
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

def update_Claim_Status(claim_id, claim_status):
    cur = conn.cursor()
    sql = """
    UPDATE claims
    SET claim_status = %s
    WHERE claim_id = %s
    """
    cur.execute(sql, (claim_status, claim_id))
    conn.commit()
    cur.close()

def select_cus_accounts(cpr_number):
    cur = conn.cursor()
    sql = """
    SELECT * FROM accounts
    NATURAL JOIN customers c
    LEFT OUTER JOIN employees e ON m.emp_cpr_number = e.id
    WHERE cpr_number = %s
    ;
    """
    cur.execute(sql, (cpr_number,))
    tuple_resultset = cur.fetchall()
    cur.close()
    return policies
