import string, random, traceback
from flask import session, render_template, redirect, url_for

from payments import app
from payments.util import form
from payments.persistence import lookup_ref

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
    errors += form.to_session('what')
    errors += form.to_session('account')
    errors += form.to_session('amount')
        
    if len(errors) == 0:
        return redirect(url_for('method'))
    else:
        return render_template('start.html', errors = errors)

@app.route('/method', methods=['GET'])
def method():
    return render_template('method.html')

@app.route('/method', methods=['POST'])
def method_submit():
    errors = form.to_session('method')
    
    if len(errors) == 0:
        if session['method'] == 'gocardless':
            return redirect(url_for('gocardless'))
        
        if session['method'] == 'stripe':
            return redirect(url_for('stripe'))
        
        if session['method'] == 'paypal':
            return redirect(url_for('paypal'))
        
#         elif payment_type =='bitcoin':
#             return redirect(url_for('bitcoin'))
        
        return redirect(url_for('method'))
    else:
        return render_template('method.html', errors = errors)

@app.route('/status/<ref>')
def status(ref):
    return render_template('status.html', payment = lookup_ref(ref))

@app.errorhandler(Exception)
def catch_all(e):
    return render_template('error.html', error = e.__class__.__name__, detail = str(e), traceback = traceback.format_exc())
