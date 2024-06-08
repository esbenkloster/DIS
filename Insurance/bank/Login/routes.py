from flask import render_template, url_for, flash, redirect, request, Blueprint, session
from bank import app, conn, bcrypt
from bank.forms import CustomerLoginForm, EmployeeLoginForm, DirectCustomerLoginForm, ForgotPasswordForm
from flask_login import login_user, current_user, logout_user, login_required
from bank.models import *

## from bank.models import select_Employee
## from bank.models import Customers, select_Customer, select_customer_direct
## from bank.models import select_cus_accounts, select_customers_direct

from bank import roles, mysession

Login = Blueprint('Login', __name__)

posts = [{}]

@Login.route("/forgot_password", methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers WHERE email = %s", (form.email.data,))
        customer = cursor.fetchone()
        if customer:
            flash('Thank you. A password reset link has been sent to your email.', 'success')
        else:
            flash('No account has been registered with that email.', 'danger')
    return render_template('forgot_password.html', title='Forgot Password', form=form, current_page='forgot_password')


@Login.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('Login.home'))
    return redirect(url_for('Login.login'))

@Login.route("/home")
@login_required
def home():
    mysession["state"] = "home"
    print(mysession)
    role = mysession["role"]
    print('role: ' + role)
    return render_template('home.html', posts=posts, role=role, current_page='home')

@Login.route("/login", methods=['GET', 'POST'])
def login():
    mysession["state"] = "login"
    print(mysession)
    role = None

    if current_user.is_authenticated:
        return redirect(url_for('Login.home'))

    is_employee = True if request.args.get('is_employee') == 'true' else False
    form = EmployeeLoginForm() if is_employee else CustomerLoginForm()

    if form.validate_on_submit():
        user = select_Employee(form.id.data) if is_employee else select_Customer(form.id.data)

        if user is not None and user[2] == form.password.data:
            print("role:" + user.role)
            if user.role == 'employee':
                mysession["role"] = roles[1]  # employee
            elif user.role == 'customer':
                mysession["role"] = roles[2]  # customer
            else:
                mysession["role"] = roles[0]  # ingen

            mysession["id"] = form.id.data
            print(mysession)
            print(roles)

            login_user(user, remember=form.remember.data)
            flash('Login successful.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('Login.home'))
        else:
            flash('Login Unsuccessful. Please check identifier and password', 'danger')

    return render_template('login.html', title='Login', is_employee=is_employee, form=form, role=role, current_page='login')

@Login.route("/about")
def about():
    mysession["state"] = "about"
    print(mysession)
    return render_template('about.html', title='About', current_page='about')

@Login.route("/direct", methods=['GET', 'POST'])
def direct():
    mysession["state"] = "direct"
    print("L1", mysession)
    role = None

    if current_user.is_authenticated:
        return redirect(url_for('Login.home'))

    is_employee = True if request.args.get('is_employee') == 'true' else False
    form = DirectCustomerLoginForm()

    if form.validate_on_submit():
        user = select_customer_direct(form.p.data)
        print("L2 user", user)

        if user is not None:
            print("L3 role:" + user.role)
            mysession["role"] = roles[2]  # customer
            mysession["id"] = form.p.data
            print("L3", mysession)
            print("L3", roles)

            login_user(user, remember=form.remember.data)
            flash('Login successful.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('Login.home'))
        else:
            flash('Login Unsuccessful. Please check identifier and password', 'danger')

    direct_users = select_customers_direct()
    print("L2 direct", direct_users)

    teachers = [{"id": str(6234), "name": "anders. teachers with 6."}, {"id": str(6214), "name": "simon"},
                {"id": str(6862), "name": "dmitry"}, {"id": str(6476), "name": "finn"}]
    parents = [{"id": str(4234), "name": "parent-anders. parents with 4.", "address": "address 1"},
               {"id": str(5002), "name": "parent-simon", "address": "address 2"},
               {"id": str(4862), "name": "parent-dmitry", "address": "address 3"},
               {"id": str(5010), "name": "parent-finn", "address": "address 4"}]
    students = [{"id": str(5002), "name": "student-anders. students with 5."}, {"id": str(5214), "name": "student-simon"},
                {"id": str(5010), "name": "student-dmitry"}, {"id": str(5476), "name": "student-finn"}]

    return render_template('direct.html', title='Direct Login', is_employee=is_employee, form=form,
                           students=students, radio_direct=direct_users, role=role, current_page='direct')

@Login.route("/logout")
def logout():
    mysession["state"] = "logout"
    print(mysession)
    logout_user()
    session.clear()
    return redirect(url_for('Login.home'))

@Login.route("/account")
@login_required
def account():
    mysession["state"] = "account"
    print(mysession)
    role = mysession["role"]
    print('role: ' + role)

    try:
        customer_id = current_user.get_id()
        customer = select_Customer(customer_id)
        policies = select_Customer_Policies(customer_id)
        print('balance: ' + str(customer.balance))  # Convert balance to string
        claims = []
        for policy in policies:
            claims += select_Policy_Claims(policy.policy_number)
        payments = []
        for policy in policies:
            payments += select_Policy_Payments(policy.policy_number)

        return render_template('account.html', title='Account', customer=customer, policies=policies, claims=claims, payments=payments, role=role, current_page='account')
    except Exception as e:
        flash('An error occurred while fetching account information.', 'danger')
        print(f"Error fetching account info: {e}")
        return redirect(url_for('Login.home'))