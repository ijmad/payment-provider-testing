import json, requests, os, datetime
from requests.auth import HTTPBasicAuth
from payments.persistence import payments_db

auth = HTTPBasicAuth(os.environ['GOCARDLESS_USER'], os.environ['GOCARDLESS_PASS'])
headers = { 'content-type': 'application/json', 'GoCardless-Version': '2014-11-03' }

class GoCardlessError(Exception):
    def __init__(self, status_code, json):
        self.status_code = status_code
        self.json = json
        
    def __str__(self):
        return repr(self.json)

def get_request(resource, resource_id):
    url = 'https://api-sandbox.gocardless.com/' + resource + '/' + resource_id
    r = requests.get(url, headers=headers, auth=auth)
    
    if r.status_code < 200 or r.status_code >= 300:
        raise GoCardlessError(r.status_code, r.json())
    else:
        return r.json()

def list_request(resource, query):
    url = 'https://api-sandbox.gocardless.com/' + resource + '?' + query
    r = requests.get(url, headers=headers, auth=auth)
    
    if r.status_code < 200 or r.status_code >= 300:
        raise GoCardlessError(r.status_code, r.json())
    else:
        return r.json()

def post_request(resource, payload):
    url = 'https://api-sandbox.gocardless.com/' + resource
    r = requests.post(url, data=json.dumps(payload), headers=headers, auth=auth)
    
    if r.status_code < 200 or r.status_code >= 300:
        raise GoCardlessError(r.status_code, r.json())
    else:
        return r.json()
    
def put_request(resource, resource_id, payload):
    url = 'https://api-sandbox.gocardless.com/' + resource + '/' + resource_id
    r = requests.put(url, data=json.dumps(payload), headers=headers, auth=auth)
    
    if r.status_code < 200 or r.status_code >= 300:
        raise GoCardlessError(r.status_code, r.json())
    else:
        return r.json()

def create_creditor(name, address, city, postcode):
    payload = {
      "creditors": {
        "name": name,
        "address_line1": address,
        "city": city,
        "postal_code": postcode,
        "country_code": "GB"
      }
    }
    
    return post_request('creditors', payload)['creditors']

def create_customer(email, firstname, lastname, address1, address2, city, postcode):
    payload = {
      "customers": {
        "email": email,
        "given_name": firstname,
        "family_name": lastname,
        "address_line1": address1,
        "address_line2": address2,
        "city": city,
        "postal_code": postcode,
        "country_code": "GB",
      }
    }
    
    return post_request('customers', payload)['customers']

def update_customer(customer_id, email, firstname, lastname, address1, address2, city, postcode):
    payload = {
      "customers": {
        "email": email,
        "given_name": firstname,
        "family_name": lastname,
        "address_line1": address1,
        "address_line2": address2,
        "city": city,
        "postal_code": postcode,
        "country_code": "GB",
      }
    }
    
    return put_request('customers', customer_id, payload)['customers']
    
def get_customer(customer_id):
    return get_request('customers', customer_id)['customers']
    
def create_bank_account(ac_number, sortcode, name, customer_id):
    payload = {
      "customer_bank_accounts": {
        "account_number": ac_number,
        "sort_code": sortcode,
        "account_holder_name": name,
        "country_code": "GB",
        "links": {
          "customer": customer_id
        }
      }
    }
    
    return post_request('customer_bank_accounts', payload)['customer_bank_accounts']
    
def disable_bank_account(account_id):
    url = 'https://api-sandbox.gocardless.com/customer_bank_accounts/%s/actions/disable' % account_id
    r = requests.post(url, headers=headers, auth=auth)
    
    if r.status_code < 200 or r.status_code >= 300:
        raise GoCardlessError(r.status_code, r.json())
    else:
        return r.json()
    

    
def get_bank_accounts(customer_id):
    return list_request('customer_bank_accounts', 'customer=' + customer_id)['customer_bank_accounts']



def get_bank_account(account_id):
    return get_request('customer_bank_accounts', account_id)['customer_bank_accounts']
    
def create_mandate(bank_account_id, creditor_id):
    payload = {
      "mandates": {
        "scheme": "bacs",
        "links": {
          "customer_bank_account": bank_account_id,
          "creditor": creditor_id
        }
      }
    }
    
    return post_request('mandates', payload)['mandates']

def list_mandates(account_id, creditor_id):
    return list_request(
      'mandates',
      'customer_bank_account=' + account_id + '&creditor=' + creditor_id
    )['mandates']

def create_payment(ref, amount, mandate_id):
    payload = {
      "payments": {
        "amount": amount,
        "currency": "GBP",
        "reference": ref,
        "links": {
          "mandate": mandate_id
        }
      }
    }
    
    return post_request('payments', payload)['payments']


def calc_payment_date(ref, customer_id, account_id, sort_code, account_number):
    if customer_id:
        if account_id and sort_code == '******' and account_number[0:6] == '******':
            account = get_bank_account(account_id) # existing account
            
            # is there a mandate for this account?
            mandates = list_mandates(account['id'], 'CR000031TY2K9C')
            active_mandate = None
            for mandate in mandates:
                if mandate['status'] == 'active':
                    # there's an active mandate!
                    active_mandate = mandate
                    break
                    
            if active_mandate:
                return (active_mandate, active_mandate['next_possible_charge_date'])
            
    return (None, (datetime.datetime.now() + datetime.timedelta(days = 10)).date())


'''
Top level make_payment function - use this one
'''
def make_payment(ref, account, amount, what, customer_id, first_name, last_name, address1, address2, city, county, postcode, account_id, sort_code, account_number, email):
    # is there an existing customer?
    if customer_id:
        customer = update_customer(
          customer_id,
          email,
          first_name,
          last_name,
          address1,
          address2,
          city,
          postcode
        )
    else:
        # create customer
        customer = create_customer(
          email,
          first_name,
          last_name,
          address1,
          address2,
          city,
          postcode
        )
    
    if account_id and sort_code == '******' and account_number[0:6] == '******':
        customer_account = get_bank_account(account_id) # unchanged
    else:
        try: 
            customer_account = create_bank_account(
              account_number,
              sort_code,
              first_name + ' ' + last_name,
              customer['id']
            )
        except GoCardlessError, e:
            if (e.json['error']['code'] == 409) and (e.json['error']['errors'][0]['reason'] == 'bank_account_exists'):
                customer_account = get_bank_account(e.json['error']['errors'][0]['links']['customer_bank_account']) 
            else:
                raise e
        
    # is there a mandate for this account?
    mandates = list_mandates(customer_account['id'], 'CR000031TY2K9C')
    active_mandate = None
    for mandate in mandates:
        if mandate['status'] == 'active':
            # there's an active mandate!
            active_mandate = mandate
            break
            
    if active_mandate:
        payment = create_payment(ref, int(amount) * 100, active_mandate['id'])
        details = {
            '_id' : ref,
            'provider' : 'gocardless',
            'what' : what,
            'account' : account,
            'amount' : amount,
            'provider_specific' : {
                'email' : email,
                'account' : customer_account,
                'mandate' : mandate,
                'payment' : payment
            }
        }
        
        # store charge 
        payments_db.insert(details)
    
    else:
        details = {
            '_id' : ref,
            'provider' : 'gocardless',
            'what' : what,
            'account' : account,
            'amount' : amount,
            'provider_specific' : {
                'email' : email,
                'account' : customer_account
            }
        }
        
        payments_db.insert(details)