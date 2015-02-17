import json, requests
from requests.auth import HTTPBasicAuth
from payments.config import gocardless_user, gocardless_pass


auth = HTTPBasicAuth(gocardless_user, gocardless_pass)
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

def create_payment(ref, amount, charge_date, mandate_id):
    payload = {
      "payments": {
        "amount": amount,
        "currency": "GBP",
        "charge_date": charge_date,
        "reference": ref,
        "links": {
          "mandate": mandate_id
        }
      }
    }
    
    return post_request('payments', payload)['payments']

