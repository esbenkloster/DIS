from flask import render_template, url_for, flash, redirect, request, Blueprint
from bank import app, conn, bcrypt
from bank.forms import PaymentForm, ClaimForm
from flask_login import current_user, login_required
from bank.models import *
import datetime
from bank import roles, mysession

iEmployee = 1
iCustomer = 2

Customer = Blueprint('Customer', __name__)

@Customer.route('/claims')
@login_required
def claims():
    if not current_user.is_authenticated:
        flash('Please login.', 'danger')
        return redirect(url_for('Login.login'))

    try:
        customer_id = current_user.get_id()
        policies = select_Customer_Policies(customer_id)
        claims = []
        for policy in policies:
            claims += select_Policy_Claims(policy.policy_number)

        return render_template('claims.html', title='Claims', claims=claims, current_page='claims')
    except Exception as e:
        flash('An error occurred while fetching claims information.', 'danger')
        print(f"Error fetching claims info: {e}")
        return redirect(url_for('Login.home'))
    
@Customer.route('/file_claim', methods=['GET', 'POST'])
@login_required
def file_claim():
    if not current_user.is_authenticated:
        flash('Please login.', 'danger')
        return redirect(url_for('Login.login'))

    if request.method == 'POST':
        policy_number = request.form['policy_number']
        claim_date = datetime.now()
        amount = request.form['amount']
        description = request.form['description']

        try:
            insert_Claim(policy_number, claim_date, amount, description)
            flash('Claim filed successfully!', 'success')
            return redirect(url_for('Customer.claims'))
        except Exception as e:
            flash('An error occurred while filing the claim. Please try again.', 'danger')
            print(f"Error filing claim: {e}")

    policies = select_Customer_Policies(current_user.get_id())
    return render_template('file_claim.html', title='File New Claim', policies=policies, current_page='claims')

@Customer.route('/payments')
@login_required
def payments():
    if not current_user.is_authenticated:
        flash('Please login.', 'danger')
        return redirect(url_for('Login.login'))

    try:
        customer_id = current_user.get_id()
        policies = select_Customer_Policies(customer_id)
        payments = []
        for policy in policies:
            payments += select_Policy_Payments(policy.policy_number)

        return render_template('payments.html', title='Payments', payments=payments, current_page='payments')
    except Exception as e:
        flash('An error occurred while fetching payment information.', 'danger')
        print(f"Error fetching payments info: {e}")
        return redirect(url_for('Login.home'))


@Customer.route("/policies", methods=['GET', 'POST'])
@login_required
def view_policies():
    mysession["state"] = "policies"
    print(f"Session state: {mysession}")

    try:
        customer_id = current_user.get_id()
        print(f"Customer ID: {customer_id}")
        policies = select_Customer_Policies(customer_id)
        print(f"Policies: {policies}")
        available_policies = select_available_policies(customer_id)
        print(f"Available Policies: {available_policies}")
        return render_template('policies.html', title='My Policies', policies=policies, available_policies=available_policies, current_page='policies')
    except Exception as e:
        flash('An error occurred while fetching policies information.', 'danger')
        print(f"Error fetching policies info: {e}")
        return redirect(url_for('Login.home'))




@Customer.route('/account')
@login_required
def account():
    session["state"] = "account"
    print(f"Session state: {session}")
    role = session.get("role", "Not assigned")
    print(f"Role: {role}")

    if role != roles[2]:  # Check if role is customer
        flash('Account view is for customers only.', 'danger')
        return redirect(url_for('Login.login'))

    try:
        customer_id = current_user.get_id()
        customer = select_Customer(customer_id)
        policies = select_Customer_Policies(customer_id)
        claims = select_Policy_Claims()
        payments = select_Policy_Payments()

        print(f"Customer Info: {customer}")
        return render_template('account.html', title='My Account', customer=customer, policies=policies, claims=claims, payments=payments)
    except Exception as e:
        flash('An error occurred while fetching account information.', 'danger')
        print(f"Error fetching account info: {e}")
        return redirect(url_for('Login.home'))


@Customer.route('/update_details', methods=['POST'])
@login_required
def update_details():
    try:
        cur = conn.cursor()
        
        print(f"Updating details: Address={request.form['address']}, Phone Number={request.form['phone_number']}, Email={request.form['email']}")

        update_sql = """
        UPDATE customers
        SET address = %s,
            phone_number = %s,
            email = %s
        WHERE CPR_number = %s
        """

        cur.execute(update_sql, (request.form['address'], request.form['phone_number'], request.form['email'], current_user.CPR_number))
        conn.commit()
        cur.close()

        flash('Your details have been updated successfully.', 'success')
    except Error as e:
        print(f"Database error: {e}")
        flash('An error occurred while updating your details. Please try again.', 'danger')

    return redirect(url_for('Customer.account'))

@Customer.route('/purchase_policy/<policy_type>', methods=['GET', 'POST'])
@login_required
def purchase_policy(policy_type):
    if not current_user.is_authenticated:
        flash('Please login.', 'danger')
        return redirect(url_for('Login.login'))

    if not mysession["role"] == roles[iCustomer]:
        flash('Policy purchase is for customers only.', 'danger')
        return redirect(url_for('Login.login'))

    try:
        new_policy_number = 'P' + str(datetime.datetime.now().timestamp()).replace('.', '')

        insert_Policy(current_user.get_id(), policy_type, 1000, 5000)  
        flash(f'You have successfully purchased the {policy_type} policy.', 'success')
        return redirect(url_for('Customer.view_policies'))
    except Exception as e:
        flash('An error occurred while purchasing the policy. Please try again.', 'danger')
        print(f"Error purchasing policy: {e}")
        return redirect(url_for('Customer.view_policies'))