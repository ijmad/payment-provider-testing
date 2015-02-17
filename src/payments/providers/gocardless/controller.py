from flask import Blueprint, session, render_template, redirect

from payments.util import form
from payments.providers.gocardless import model

gocardless_bp = Blueprint('gocardless', __name__, template_folder='templates')

@gocardless_bp.route('/', methods=["GET"])
def gocardless():
    return redirect(('.signin'))

@gocardless_bp.route('/signin', methods=["GET"])
def gocardless_signin():
    return render_template('signin.html')

@gocardless_bp.route('/gocardless-signin', methods=["POST"])
def gocardless_signin_submit():
    # fudge - pre-known customer id
    session['customer_id'] = 'CU00002TDW4R84'
    
    customer = model.get_customer(session['customer_id'])
    accounts = model.get_bank_accounts(session['customer_id'])

    if len(accounts) > 0:
        session['account_id'] = accounts[0]['id'] 
        session['sort-code'] = '******'
        session['account-number'] = '******' + accounts[0]['account_number_ending']
        
    session['first-name'] = customer['given_name']
    session['last-name'] = customer['family_name']
    session['address-street-1'] = customer['address_line1']
    session['address-street-2'] = customer['address_line2']
    session['address-city'] = customer['city']
    session['address-county'] = customer['region']
    session['address-postcode'] = customer['postal_code']
    session['email'] = customer['email']
    
    return redirect(('.gocardless_details'))

@gocardless_bp.route('/details', methods=["GET"])
def gocardless_details():
    return render_template('details.html')

@gocardless_bp.route('/gocardless-details', methods=["POST"])
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
        return render_template('details.html', errors = errors)
    else:
        return redirect(('.gocardless_confirm'))

@gocardless_bp.route('/confirm', methods=["GET"])
def gocardless_confirm():
    return render_template('confirm.html')

@gocardless_bp.route('/confirm', methods=['POST'])
def gocardless_confirm_submit():
    errors = []
    errors += form.to_session('email')
    
    if len(errors) != 0:
        return render_template('confirm.html', errors = errors)
    else:
        # is there an existing customer?
        if 'customer_id' in session:
            customer = model.update_customer(
              session['customer_id'],
              session['email'],
              session['first-name'],
              session['last-name'],
              session['address-street-1'],
              session['address-street-2'],
              session['address-city'],
              session['address-postcode']
            )
        else:
            # create customer
            customer = model.create_customer(
              session['email'],
              session['first-name'],
              session['last-name'],
              session['address-street-1'],
              session['address-street-2'],
              session['address-city'],
              session['address-postcode']
            )
        
        if 'account_id' in session and session['sort-code'] == '******' and session['account-number'][0:6] == '******':
            account = model.get_bank_account(session['account_id']) # unchanged
        else:
            try: 
                account = model.create_bank_account(
                  session['account-number'],
                  session['sort-code'],
                  session['first-name'] + ' ' + session['last-name'],
                  customer['id']
                )
            except model.GoCardlessError, e:
                if (e.json['error']['code'] == 409) and (e.json['error']['errors'][0]['reason'] == 'bank_account_exists'):
                    account = model.get_bank_account(e.json['error']['errors'][0]['links']['customer_bank_account']) 
                else:
                    raise e
            
        # is there a mandate for this account?
        mandates = model.list_mandates(account['id'], 'CR000031TY2K9C')
        return repr(mandates)
        
#         payment = model.create_payment(session['ref'], session['amount'], charge_date, mandate['id'])
#         return "OK"