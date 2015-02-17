from flask import request, session, render_template, redirect, url_for

from payments import app
from payments.providers.paypal import model

@app.route('/paypal', methods=["GET"])
def paypal():
    return render_template('paypal/paypal.html')

@app.route('/paypal', methods=["POST"])
def paypal_submit():
    redirect_url = model.make_payment(session['ref'], session['amount'], session['account'], session['what'])
    return redirect(redirect_url)

@app.route('/paypal/landing/return')
def paypal_return():
    ref = model.success(request.args.get('paymentId'), request.args.get('PayerID'))
    return redirect(url_for('status', ref = ref))

@app.route('/paypal/landing/cancel')
def paypal_cancel():
    ref = model.cancelled(request.args.get('paymentId'))
    return redirect(url_for('status', ref = ref))