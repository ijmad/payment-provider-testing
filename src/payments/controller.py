import string, random

from payments import app
from flask import render_template, redirect, url_for
from form import *
from payments.providers import stripeuk_model, paypal_model, gocardless_model
from lookup_model import lookup_ref



@app.route('/', methods=['GET'])
def index():
    session.clear()
    return redirect(url_for('start'))



@app.route('/start', methods=['GET'])
def start():
    def rand4():
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    session['ref'] = '%s-%s-%s-%s' % (rand4(), rand4(), rand4(), rand4()) 
    return render_template('start.html')



@app.route('/start', methods=['POST'])
def start_submit():
    errors = []
    errors += handle_form_var('what')
    errors += handle_form_var('account')
    errors += handle_form_var('amount')
        
    if len(errors) == 0:
        return redirect(url_for('method'))
    else:
        return render_template('start.html', errors = errors)



@app.route('/method', methods=['GET'])
def method():
    return render_template('method.html')



@app.route('/method', methods=['POST'])
def method_submit():
    errors = handle_form_var('method')
    
    if len(errors) == 0:
        if session['method'] == 'dd':
            return redirect(url_for('dd_signin'))
        
        if session['method'] == 'card':
            return redirect(url_for('card_details'))
        
        if session['method'] == 'paypal':
            return redirect(url_for('paypal'))
        
#         elif payment_type =='bitcoin':
#             return redirect(url_for('bitcoin'))
        
        return redirect(url_for('method'))
    else:
        return render_template('method.html', errors = errors)
    






@app.route('/paypal', methods=["GET"])
def paypal():
    return render_template('paypal.html')



@app.route('/paypal', methods=["POST"])
def paypal_submit():
    redirect_url = paypal_model.make_payment(session['ref'], session['amount'], session['account'], session['what'])
    return redirect(redirect_url)



@app.route('/landing/paypal/return')
def paypal_return():
    ref = paypal_model.success(request.args.get('paymentId'), request.args.get('PayerID'))
    return redirect('status', ref = ref)



@app.route('/landing/paypal/cancel')
def paypal_cancel():
    ref = paypal_model.cancelled(request.args.get('paymentId'))
    return redirect('status', ref = ref)











@app.route('/dd-signin', methods=["GET"])
def dd_signin():
    return render_template('dd-signin.html')

@app.route('/dd-signin', methods=["POST"])
def dd_signin_submit():
    # fudge - pre-known customer id
    session['customer_id'] = 'CU00002TDW4R84'
    
    customer = gocardless_model.get_customer(session['customer_id'])
    accounts = gocardless_model.get_bank_accounts(session['customer_id'])

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
    
    return redirect(url_for('dd_details'))

@app.route('/dd-details', methods=["GET"])
def dd_details():
    return render_template('dd-details.html')



@app.route('/dd-details', methods=["POST"])
def dd_details_submit():
    errors = []
    errors += handle_form_var('sort-code')
    errors += handle_form_var('account-number')
    errors += handle_form_var_boolean('account-multi')
    errors += handle_form_var('first-name')
    errors += handle_form_var('last-name')
    errors += handle_form_var('address-street-1')
    errors += handle_form_var('address-street-2', False)
    errors += handle_form_var('address-city')
    errors += handle_form_var('address-county')
    errors += handle_form_var('address-postcode')
    
    if len(errors) != 0:
        print errors
        return render_template('dd-details.html', errors = errors)
    else:
        return redirect(url_for('dd_confirm'))



@app.route('/dd-confirm', methods=["GET"])
def dd_confirm():
    return render_template('dd-confirm.html')



@app.route('/dd-confirm', methods=['POST'])
def dd_confirm_submit():
    errors = []
    errors += handle_form_var('email')
    
    if len(errors) != 0:
        return render_template('dd-confirm.html', errors = errors)
    else:
        # is there an existing customer?
        if 'customer_id' in session:
            customer = gocardless_model.update_customer(
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
            customer = gocardless_model.create_customer(
              session['email'],
              session['first-name'],
              session['last-name'],
              session['address-street-1'],
              session['address-street-2'],
              session['address-city'],
              session['address-postcode']
            )
        
        if 'account_id' in session and session['sort-code'] == '******' and session['account-number'][0:6] == '******':
            account = gocardless_model.get_bank_account(session['account_id']) # unchanged
        else:
            try: 
                account = gocardless_model.create_bank_account(
                  session['account-number'],
                  session['sort-code'],
                  session['first-name'] + ' ' + session['last-name'],
                  customer['id']
                )
            except gocardless_model.GoCardlessError, e:
                if (e.json['error']['code'] == 409) and (e.json['error']['errors'][0]['reason'] == 'bank_account_exists'):
                    account = gocardless_model.get_bank_account(e.json['error']['errors'][0]['links']['customer_bank_account']) 
                else:
                    raise e
            
        # is there a mandate for this account?
        mandates = gocardless_model.list_mandates(account['id'], 'CR000031TY2K9C')
        return repr(mandates)
        
#         payment = gocardless_model.create_payment(session['ref'], session['amount'], charge_date, mandate['id'])
#         return "OK"


@app.route('/card-details', methods=['GET'])
def card_details():
    return render_template('card-details.html')



@app.route('/card-details', methods=['POST'])
def card_details_submit():
    errors = []
    errors += handle_form_var('card-type')
    errors += handle_form_var('card-number')
    errors += handle_form_var('card-name')
    errors += handle_form_var('card-expiry-month')
    errors += handle_form_var('card-expiry-year')
    errors += handle_form_var('card-csc')
    errors += handle_form_var('card-address-street-1')
    errors += handle_form_var('card-address-street-2', False)
    errors += handle_form_var('card-address-city')
    errors += handle_form_var('card-address-county', False)
    errors += handle_form_var('card-address-postcode')
    
    if len(errors) != 0:
        return render_template('card-details.html', errors = errors)
    else:
        return redirect(url_for('card_confirm'))



@app.route('/card-confirm', methods=['GET'])
def card_confirm():
    return render_template('card-confirm.html')



@app.route('/card-confirm', methods=['POST'])
def card_confirm_submit():
    errors = []
    errors += handle_form_var('email')
    
    if len(errors) != 0:
        return render_template('card-confirm.html', errors = errors)
    else:
        ref = session['ref']
        
        # submit payment!
        stripeuk_model.make_payment(
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



@app.route('/status/<ref>')
def status(ref):
    return render_template('status.html', payment = lookup_ref(ref))



@app.errorhandler(Exception)
def catch_all(e):
    return render_template('error.html', error = str(e))



if __name__ == '__main__':
    app.run(debug = True)