from flask import Blueprint, session, render_template, redirect, url_for

from payments.util import form
from payments.providers.gocardless import model
from payments.persistence import lookup_ref

gocardless_bp = Blueprint('gocardless', __name__, template_folder='templates')

@gocardless_bp.route('/', methods=["GET"])
def gocardless():
    return redirect(url_for('.gocardless_signin'))

@gocardless_bp.route('/signin', methods=["GET"])
def gocardless_signin():
    return render_template('gocardless_signin.html')

@gocardless_bp.route('/signin', methods=["POST"])
def gocardless_signin_submit():
    # fudge - pre-known customer id
    session['customer_id'] = 'CU00002TDW4R84'
    
    customer = model.get_customer(session['customer_id'])
    accounts = model.get_bank_accounts(session['customer_id'])

    if len(accounts) > 0:
        for account in accounts:
            if account['enabled']:
                session['account_id'] = account['id'] 
                session['sort-code'] = '******'
                session['account-number'] = '******' + account['account_number_ending']
                break
        
    session['first-name'] = customer['given_name']
    session['last-name'] = customer['family_name']
    session['address-street-1'] = customer['address_line1']
    session['address-street-2'] = customer['address_line2']
    session['address-city'] = customer['city']
    session['address-county'] = customer['region']
    session['address-postcode'] = customer['postal_code']
    session['email'] = customer['email']
    
    return redirect(url_for('.gocardless_details'))

@gocardless_bp.route('/details', methods=["GET"])
def gocardless_details():
    return render_template('gocardless_details.html')

@gocardless_bp.route('/details', methods=["POST"])
def gocardless_details_submit():
    errors = []
    errors += form.to_session('sort-code')
    errors += form.to_session('account-number')
    errors += form.to_session_bool('account-multi')
    errors += form.to_session('first-name')
    errors += form.to_session('last-name')
    errors += form.to_session('address-street-1')
    errors += form.to_session('address-street-2', False)
    errors += form.to_session('address-city')
    errors += form.to_session('address-county')
    errors += form.to_session('address-postcode')
    
    if len(errors) != 0:
        print errors
        return render_template('gocardless_details.html', errors = errors)
    else:
        return redirect(url_for('.gocardless_confirm'))

@gocardless_bp.route('/confirm', methods=["GET"])
def gocardless_confirm():
    (mandate, charge_date) = model.calc_payment_date(
      session['ref'],
      session.get('customer_id', None),
      session.get('account_id', None),
      session['sort-code'],
      session['account-number']
    )
    
    return render_template('gocardless_confirm.html', mandate = mandate, charge_date = charge_date)

@gocardless_bp.route('/confirm', methods=['POST'])
def gocardless_confirm_submit():
    errors = []
    errors += form.to_session('email')
    
    if len(errors) != 0:
        return render_template('gocardless_confirm.html', errors = errors)
    else:
        model.make_payment(
          session['ref'],
          session['account'],
          session['amount'],
          session['what'],
          session.get('customer_id', None),
          session['first-name'],
          session['last-name'],
          session['address-street-1'],
          session['address-street-2'],
          session['address-city'],
          session['address-county'],
          session['address-postcode'],
          session.get('account_id', None),
          session['sort-code'],
          session['account-number'],
          session['email']
        )
        
        return redirect(url_for('.gocardless_status', ref=session['ref']))
    
@gocardless_bp.route('/status/<ref>', methods=['GET'])
def gocardless_status(ref):
    return render_template('gocardless_status.html', payment = lookup_ref(ref))
        
        
        
        
        