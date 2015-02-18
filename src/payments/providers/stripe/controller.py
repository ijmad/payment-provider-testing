from flask import Blueprint, session, render_template, url_for, redirect

from payments.providers.stripe import model
from payments.persistence import lookup_ref
from payments.util import form
from payments.util.session import session_required
 
stripe_bp = Blueprint('stripe', __name__, template_folder='templates')

@stripe_bp.route('/', methods=["GET"])
@session_required
def stripe():
    return redirect(url_for('.stripe_details'))

@stripe_bp.route('/details', methods=['GET'])
@session_required
def stripe_details():
    return render_template('stripe_details.html')

@stripe_bp.route('/details', methods=['POST'])
@session_required
def stripe_details_submit():
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
        return render_template('stripe_details.html', errors = errors)
    else:
        return redirect(url_for('.stripe_confirm'))

@stripe_bp.route('/confirm', methods=['GET'])
@session_required
def stripe_confirm():
    return render_template('stripe_confirm.html')

@stripe_bp.route('/confirm', methods=['POST'])
@session_required
def stripe_confirm_submit():
    errors = []
    errors += form.to_session('email')
    
    if len(errors) != 0:
        return render_template('stripe_confirm.html', errors = errors)
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
    
@stripe_bp.route('/status/<ref>', methods=['GET'])
def stripe_status(ref):
    return render_template('stripe_status.html', payment = lookup_ref(ref))