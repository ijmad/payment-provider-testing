import string, random, traceback
from flask import session, render_template, redirect, url_for, abort

from payments.main import app
from payments.persistence import lookup_ref
from payments.util import form

@app.route('/', methods=['GET'])
def index():
    session.clear()
    return redirect(url_for('start'))

@app.route('/start', methods=['GET'])
def start():
    def rand(length):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))
    session['ref'] = '%s-%s' % (rand(4), rand(4)) 
    return render_template('start.html')

@app.route('/start', methods=['POST'])
def start_submit():
    errors = []
    errors += form.to_session('what')
    errors += form.to_session('account')
    errors += form.to_session('amount')
        
    if len(errors) == 0:
        return redirect(url_for('provider'))
    else:
        return render_template('start.html', errors = errors)

@app.route('/provider', methods=['GET'])
def provider():
    return render_template('provider.html')

@app.route('/provider', methods=['POST'])
def provider_submit():
    errors = form.to_session('provider')
    
    if len(errors) == 0:
        if session['provider'] == 'stripe':
            return redirect(url_for('stripe.stripe'))
        
        if session['provider'] == 'gocardless':
            return redirect(url_for('gocardless.gocardless'))
        
        if session['provider'] == 'paypal':
            return redirect(url_for('paypal.paypal'))
        
        return redirect(url_for('provider'))
    else:
        return render_template('provider.html', errors = errors)

@app.route('/status/<ref>')
def status(ref):
    payment = lookup_ref(ref)    
    if payment['provider'] == 'stripe':
        return redirect(url_for('stripe.stripe_status', ref = ref))
    
    if payment['provider'] == 'gocardless':
        return redirect(url_for('gocardless.stripe_status', ref = ref))
    
    if payment['provider'] == 'paypal':
        return redirect(url_for('paypal.stripe_status', ref = ref))
    
    return abort(404)

@app.errorhandler(Exception)
def catch_all(e):
    return render_template('error.html', error = e.__class__.__name__, detail = str(e), traceback = traceback.format_exc())
