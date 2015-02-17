import json, requests
from requests.auth import HTTPBasicAuth
from payments.persistence import client
from payments.config import paypal_user, paypal_pass

db = client.payments


class PayPalError(Exception):
    def __init__(self, status_code, json):
        self.status_code = status_code
        self.json = json
        
    def __str__(self):
        return repr(self.json)



def make_request(url, payload):
    headers = {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer %s' % get_token()
    }
    
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    if r.status_code < 200 or r.status_code >= 300:
        raise PayPalError(r.json()['message'])
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
      auth=HTTPBasicAuth(paypal_user, paypal_pass)
    )
    
    if r.status_code < 200 or r.status_code >= 300:
        json = r.json()
        raise PayPalError(str(json['error'] + ': ' + json['error_description'] ))
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
        "return_url" : "http://localhost:5000/landing/paypal/return",
        "cancel_url" : "http://localhost:5000/landing/paypal/cancel"
      }
    }
    
    result = make_request('https://api.sandbox.paypal.com/v1/payments/payment', payload)
    details = {
        '_id' : ref,
        'success' : False, # so far...
        'method' : 'paypal',
        'provider' : 'paypal',
        'account' : account,
        'amount' : amount,
        'what' : what,
        'result' : result
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
    cursor = db.payments.find({ 'result.id' : payment_id })
    
    if cursor.count() == 1:
        payment = cursor.next()
        
        # get the execute url
        for link in payment['result']['links']:
            if str(link['rel']) == 'execute':
                info = execute(str(link['href']), payer_id)
                db.payments.update(payment, { '$set': { 'success' : True, 'info' : info } })
                return payment['_id']
        
    raise PayPalError('Payment not found')



def cancelled(payment_id):
    cursor = db.payments.find({ 'result.id' : payment_id })
    
    if cursor.count() == 1:
        payment = cursor.next()
        db.payments.update(payment, { '$set': { 'message' : 'You cancelled the payment' } })
        return payment['_id']
    
    raise PayPalError('Payment not found')
    
