from flask import render_template, url_for, flash, redirect, request, Blueprint
from bank import conn, bcrypt
from bank.forms import PaymentForm
from flask_login import current_user
from bank.models import Policy, Claim, insert_Policy
from bank.models import select_Policy_Claims, update_Claim_Status

import datetime

from bank import roles, mysession

iEmployee = 1
iCustomer = 2

Employee = Blueprint('Employee', __name__)

@Employee.route("/process_claim/<int:claim_id>/<string:status>", methods=['POST'])
def process_claim(claim_id, status):
    if not current_user.is_authenticated:
        flash('Please login.', 'danger')
        return redirect(url_for('Login.login'))

    if not mysession["role"] == roles[iEmployee]:
        flash('Claim processing is for employees only.', 'danger')
        return redirect(url_for('Login.login'))

    update_Claim_Status(claim_id, status)
    flash(f'Claim {claim_id} has been {status}.', 'success')
    return redirect(url_for('Login.home'))

@Employee.route("/claims", methods=['GET'])
def view_claims():
    if not current_user.is_authenticated:
        flash('Please login.', 'danger')
        return redirect(url_for('Login.login'))

    if not mysession["role"] == roles[iEmployee]:
        flash('Claim view is for employees only.', 'danger')
        return redirect(url_for('Login.login'))

    claims = select_Policy_Claims()
    return render_template('claims.html', title='Claims', claims=claims)
