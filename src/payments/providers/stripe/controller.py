from flask import session, render_template, url_for, redirect

from payments import app
from payments.providers.stripe import model
from payments.util import form

@app.route('/stripe', methods=["GET"])
def stripe():
    return redirect(url_for('stripe_details'))

@app.route('/stripe_details', methods=['GET'])
def stripe_details():
    return render_template('stripe/details.html')

@app.route('/stripe_details', methods=['POST'])
def card_details_submit():
    errors = []
    errors += form.to_session('card-type')
    errors += form.to_session('card-number')
    errors += form.to_session('card-name')
    errors += form.to_session('card-expiry-month')
    errors += form.to_session('card-expiry-year')
    errors += form.to_session('card-csc')
    errors += form.to_session('card-address-street-1')
    errors += form.to_session('card-address-street-2', False)
    errors += form.to_session('card-address-city')
    errors += form.to_session('card-address-county', False)
    errors += form.to_session('card-address-postcode')
    
    if len(errors) != 0:
        return render_template('stripe/details.html', errors = errors)
    else:
        return redirect(url_for('stripe_confirm'))

@app.route('/stripe_confirm', methods=['GET'])
def stripe_confirm():
    return render_template('stripe/confirm.html')

@app.route('/stripe_confirm', methods=['POST'])
def stripe_confirm_submit():
    errors = []
    errors += form.to_session('email')
    
    if len(errors) != 0:
        return render_template('stripe/confirm.html', errors = errors)
    else:
        ref = session['ref']
        
        # submit payment!
        model.make_payment(
          session['ref'],
          session['account'],
          session['amount'],
          session['what'],
          session['card-number'],
          session['card-expiry-month'],
          session['card-expiry-year'],
          session['card-csc'],
          session['card-name'],
          session['card-address-street-1'],
          session['card-address-street-2'],
          session['card-address-city'],
          session['card-address-county'],
          session['card-address-postcode'],
          session['email']
        )
        
        # wipe session
        session.clear()
        
        # permanent status page
        return redirect(url_for('status', ref = ref))