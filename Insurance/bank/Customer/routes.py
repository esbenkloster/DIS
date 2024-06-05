from flask import render_template, url_for, flash, redirect, request, Blueprint
from bank import app, conn, bcrypt
from bank.forms import PaymentForm, ClaimForm
from flask_login import current_user
from bank.models import Policy, Claim, insert_Policy
from bank.models import select_Customer_Policies, insert_Claim, select_Policy_Claims
from bank.models import update_Claim_Status, select_cus_accounts

import datetime

from bank import roles, mysession

iEmployee = 1
iCustomer = 2

Customer = Blueprint('Customer', __name__)

@Customer.route("/claim", methods=['GET', 'POST'])
def claim():
    if not current_user.is_authenticated:
        flash('Please login.', 'danger')
        return redirect(url_for('Login.login'))

    if not mysession["role"] == roles[iCustomer]:
        flash('Claim submission is for customers only.', 'danger')
        return redirect(url_for('Login.login'))

    form = ClaimForm()
    if form.validate_on_submit():
        description = form.description.data
        amount = form.amount.data
        policy_number = request.args.get('policy_number')
        insert_Claim(policy_number, datetime.datetime.now(), amount, description)
        flash('Claim submitted successfully!', 'success')
        return redirect(url_for('Login.home'))
    return render_template('claim.html', title='Submit Claim', form=form)

@Customer.route("/policies", methods=['GET', 'POST'])
def view_policies():
    if not current_user.is_authenticated:
        flash('Please login.', 'danger')
        return redirect(url_for('Login.login'))

    if not mysession["role"] == roles[iCustomer]:
        flash('Policy view is for customers only.', 'danger')
        return redirect(url_for('Login.login'))

    policies = select_Customer_Policies(current_user.get_id())
    return render_template('policies.html', title='My Policies', policies=policies)
