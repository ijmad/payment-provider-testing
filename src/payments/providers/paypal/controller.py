from flask import Blueprint, request, session, render_template, redirect, url_for

from payments.providers.paypal import model
from payments.persistence import lookup_ref

paypal_bp = Blueprint('paypal', __name__, template_folder='templates')

@paypal_bp.route('/', methods=["GET"])
def paypal():
    return render_template('paypal.html')

@paypal_bp.route('/', methods=["POST"])
def paypal_submit():
    redirect_url = model.make_payment(session['ref'], session['amount'], session['account'], session['what'])
    return redirect(redirect_url)

@paypal_bp.route('/landing/return')
def paypal_return():
    ref = model.success(request.args.get('paymentId'), request.args.get('PayerID'))
    return redirect(url_for('status', ref = ref))

@paypal_bp.route('/landing/cancel')
def paypal_cancel():
    ref = model.cancelled(request.args.get('paymentId'))
    return redirect(url_for('status', ref = ref))

@paypal_bp.route('/status/<ref>', methods=['GET'])
def paypal_status(ref):
    return render_template('paypal_status.html', payment = lookup_ref(ref))