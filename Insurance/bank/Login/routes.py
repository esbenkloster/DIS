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

@Login.route('/home')
@login_required
def home():
    if not current_user.is_authenticated:
        flash('Please login.', 'danger')
        return redirect(url_for('Login.login'))

    try:
        customer_id = current_user.get_id()
        customer = select_Customer(customer_id)
        policies = select_Customer_Policies(customer_id)
        recent_claims = []
        recent_payments = []

        # Fetch recent claims
        for policy in policies:
            recent_claims += select_Policy_Claims(policy.policy_number)
        recent_claims = sorted(recent_claims, key=lambda x: x.claim_date, reverse=True)[:5]

        # Fetch recent payments
        for policy in policies:
            recent_payments += select_Policy_Payments(policy.policy_number)
        recent_payments = sorted(recent_payments, key=lambda x: x.payment_date, reverse=True)[:5]

        # Fetch active policies
        active_policies = [policy for policy in policies if policy.end_date > datetime.now().date()]

        # Get role from session
        role = mysession.get("role") 

        return render_template('home.html', title='Home', customer=customer, recent_claims=recent_claims, recent_payments=recent_payments, active_policies=active_policies, role=role, current_page='home')
    except Exception as e:
        flash('An error occurred while fetching home page information.', 'danger')
        print(f"Error fetching home page info: {e}")
        return redirect(url_for('Login.home'))



@Login.route("/account")
@login_required
def account():
    mysession["state"] = "account"
    print(mysession)
    role = mysession.get("role", "Not assigned")
    print('role: ' + role)

    try:
        customer_id = current_user.get_id()
        customer = select_Customer(customer_id)
        policies = select_Customer_Policies(customer_id)
        print('balance: ' + str(customer.balance)) 
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




@Login.route("/about")
def about():
    mysession["state"] = "about"
    print(mysession)

    role = mysession.get("role")

    return render_template('about.html', title='About', role=role, current_page='about')

@Login.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('Login.home'))

    is_employee = True if request.args.get('is_employee') == 'true' else False
    form = EmployeeLoginForm() if is_employee else CustomerLoginForm()

    if form.validate_on_submit():
        user = select_Employee(form.id.data) if is_employee else select_Customer(form.id.data)

        if user and user.password == form.password.data:
            if is_employee:
                mysession["role"] = 'employee'
            else:
                mysession["role"] = 'customer'

            mysession["id"] = form.id.data
            login_user(user, remember=form.remember.data)
            flash('Login successful.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('Login.home'))
        else:
            flash('Login Unsuccessful. Please check identifier and password', 'danger')

    return render_template('login.html', title='Login', is_employee=is_employee, form=form)





@Login.route("/logout")
def logout():
    mysession["state"] = "logout"
    print(mysession)
    logout_user()
    session.clear()
    return redirect(url_for('Login.home'))
