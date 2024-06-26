from flask import render_template, url_for, flash, redirect, request, Blueprint
from bank import conn, bcrypt
from bank.forms import *
from flask_login import current_user, login_required
from bank.models import *

import datetime

from bank import roles, mysession

iEmployee = 1
iCustomer = 2

Employee = Blueprint('Employee', __name__)

@Employee.route("/process_claim/<int:claim_id>/<string:status>", methods=['GET', 'POST'])
@login_required
def process_claim(claim_id, status):
    if not current_user.is_authenticated:
        flash('Please login.', 'danger')
        return redirect(url_for('Login.login'))

    if mysession.get("role") != 'employee':
        flash('Claim processing is for employees only.', 'danger')
        return redirect(url_for('Login.login'))

    try:
        update_Claim_Status(claim_id, status)
        flash(f'Claim {claim_id} has been {status}.', 'success')
    except Exception as e:
        flash(f'Error processing claim: {e}', 'danger')

    return redirect(url_for('Employee.view_claims'))

@Employee.route("/view_claims", methods=['GET'])
@login_required
def view_claims():
    if not current_user.is_authenticated:
        flash('Please login.', 'danger')
        return redirect(url_for('Login.login'))

    if mysession.get("role") != 'employee':
        flash('Claim view is for employees only.', 'danger')
        return redirect(url_for('Login.login'))
    
    try:
        employee_id = current_user.get_id()
        policies = select_Policies_Managed_By_Employee(employee_id)
        claims = []
        for policy in policies:
            claims += select_Policy_Claims(policy.policy_number)

        pending_claims = [claim for claim in claims if claim.claim_status == 'Pending']

        return render_template('process_claims.html', title='Process Claims', claims=pending_claims, role='employee', current_page='process_claims')
    except Exception as e:
        flash(f'Error fetching claims: {e}', 'danger')
        return redirect(url_for('Login.home'))

@Employee.route("/manage_customers", methods=['GET', 'POST'])
@login_required
def manage_customers():
    if not current_user.is_authenticated:
        flash('Please login.', 'danger')
        return redirect(url_for('Login.login'))

    if not mysession.get("role") == 'employee':
        flash('Customer management is for employees only.', 'danger')
        return redirect(url_for('Login.login'))

    if request.method == 'POST':
        # Handle customer update or deletion
        if 'update' in request.form:
            form = AddCustomerForm(request.form)
            if form.validate():
                update_Customer(form)
                flash('Customer updated successfully!', 'success')
        elif 'delete' in request.form:
            cpr_number = request.form['cpr_number']
            delete_Customer(cpr_number)
            flash('Customer deleted successfully!', 'success')

    customers = select_Customers()
    return render_template('manage_customers.html', title='Manage Customers', customers=customers, role=mysession.get("role"), current_page='manage_customers')

@Employee.route("/process_claims", methods=['GET'])
@login_required
def process_claims():
    if not current_user.is_authenticated:
        flash('Please login.', 'danger')
        return redirect(url_for('Login.login'))

    if not mysession.get("role") == 'employee':
        flash('Claim processing is for employees only.', 'danger')
        return redirect(url_for('Login.login'))

    claims = select_Policy_Claims(policy_number=None)
    return render_template('process_claims.html', title='Process Claims', claims=claims, role=mysession.get("role"), current_page='process_claims')

@Employee.route("/manage_policies", methods=['GET'])
@login_required
def manage_policies():
    if not current_user.is_authenticated:
        flash('Please login.', 'danger')
        return redirect(url_for('Login.login'))

    if not mysession.get("role") == 'employee':
        flash('Policy management is for employees only.', 'danger')
        return redirect(url_for('Login.login'))

    employee_id = current_user.get_id()
    policies = select_Employee_Policies(employee_id)
    return render_template('manage_policies.html', title='Manage Policies', policies=policies, role=mysession.get("role"), current_page='manage_policies')

@Employee.route("/policy_claims/<string:policy_number>", methods=['GET'])
@login_required
def view_policy_claims(policy_number):
    if not current_user.is_authenticated:
        flash('Please login.', 'danger')
        return redirect(url_for('Login.login'))

    if not mysession.get("role") == 'employee':
        flash('Claim view is for employees only.', 'danger')
        return redirect(url_for('Login.login'))

    claims = select_Policy_Claims(policy_number)
    return render_template('policy_claims.html', title='Policy Claims', claims=claims, role=mysession.get("role"), current_page='process_claims')

@Employee.route("/policy_payments/<string:policy_number>", methods=['GET'])
@login_required
def view_policy_payments(policy_number):
    if not current_user.is_authenticated:
        flash('Please login.', 'danger')
        return redirect(url_for('Login.login'))

    if not mysession.get("role") == 'employee':
        flash('Payment view is for employees only.', 'danger')
        return redirect(url_for('Login.login'))

    payments = select_Policy_Payments(policy_number)
    return render_template('policy_payments.html', title='Policy Payments', payments=payments, role=mysession.get("role"), current_page='view_payments')

@Employee.route("/customer/<int:cpr_number>", methods=['GET'])
@login_required
def view_customer(cpr_number):
    if not current_user.is_authenticated:
        flash('Please login.', 'danger')
        return redirect(url_for('Login.login'))

    if not mysession.get("role") == 'employee':
        flash('Customer view is for employees only.', 'danger')
        return redirect(url_for('Login.login'))

    customer = select_Customer(cpr_number)
    return render_template('customer_details.html', title='Customer Details', customer=customer, role=mysession.get("role"), current_page='view_customer')
