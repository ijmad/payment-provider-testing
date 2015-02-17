import json, requests, os
from flask import url_for
from requests.auth import HTTPBasicAuth
from payments.persistence import client

auth = HTTPBasicAuth(os.environ['PAYPAL_USER'], os.environ['PAYPAL_PASS'])
db = client.payments

class PayPalError(Exception):
    def __init__(self, message):
        self.message = message
        
    def __str__(self):
        return repr(self.message)

def make_request(url, payload):
    headers = {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer %s' % get_token()
    }
    
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    if r.status_code < 200 or r.status_code >= 300:
        raise PayPalError(r.json())
    else:
        return r.json()

def get_token():
    url = 'https://api.sandbox.paypal.com/v1/oauth2/token?'
    headers = {
      'Accept': 'application/json',
      'Accept-Language': 'en_US',
    }
    
    r = requests.post(
      url,
      headers=headers,
      data = {'grant_type' : 'client_credentials'},
      auth = auth
    )
    
    if r.status_code < 200 or r.status_code >= 300:
        raise PayPalError(r.json())
    else:
        return r.json()['access_token']

def make_payment(ref, amount, account, what):
    payload = {
      "intent":"sale",
      "payer":{
        "payment_method":"paypal"
      },
      "transactions":[
        {
          "description": 'Paying %s for %s to account %s' % (amount, what, account),
          "amount":{
            "total": str(amount),
            "currency":"GBP",
          }
        }
      ],
      "redirect_urls" : {
        "return_url" : url_for('paypal_return', _external = True),
        "cancel_url" : url_for('paypal_cancel', _external = True)
      }
    }
    
    result = make_request('https://api.sandbox.paypal.com/v1/payments/payment', payload)
    details = {
        '_id' : ref,
        'provider' : 'paypal',
        'what' : what,
        'account' : account,
        'amount' : amount,
        'provider_specific' : {
            'result' : result
        }
    }
    
    # store charge 
    db.payments.insert(details)
    
    # get the redirect url
    for link in result['links']:
        if str(link['rel']) == 'approval_url':
            return link['href']
        
    return None

def execute(url, payer_id):
    return make_request(url, { "payer_id" : payer_id })

def success(payment_id, payer_id):
    cursor = db.payments.find({ 'provider_specific.result.id' : payment_id })
    
    if cursor.count() == 1:
        payment = cursor.next()
        
        # get the execute url
        for link in payment['provider_specific']['result']['links']:
            if str(link['rel']) == 'execute':
                execution = execute(str(link['href']), payer_id)
                db.payments.update(payment, { '$set': { 'provider_specific.execution' : execution } })
                return payment['_id']
        
    raise PayPalError('Payment not found')

def cancelled(payment_id):
    cursor = db.payments.find({ 'result.id' : payment_id })
    
    if cursor.count() == 1:
        payment = cursor.next()
        db.payments.update(payment, { '$set': { 'message' : 'You cancelled the payment' } })
        return payment['_id']
    
    raise PayPalError('Payment not found')
    
