import stripe, os
from payments.persistence import client

db = client.payments
stripe.api_key = os.environ['STRIPE_KEY']
stripe.api_version = '2015-01-26'

def make_payment(ref, account, amount, what, card_number, exp_month, exp_year, cvc, name, address1, address2, city, county, postcode, email):
    try:
        customer = stripe.Customer.create(
          card= {
              'number': card_number,
              'exp_month': exp_month, 
              'exp_year': exp_year, 
              'cvc': cvc, 
              'name': name, 
              'address_line1': address1, 
              'address_line2': address2, 
              'address_city': city, 
              'address_zip': postcode, 
              'address_state': county, 
              'address_country': 'GB'
          }
        )
        
        charge = stripe.Charge.create(
          customer = customer.id,
          card = customer.cards.data[0].id,
          amount = int(float(amount) * 100), # pence
          currency = "gbp",
          description = 'Payment of ' + what + ' to account ' + account
        )
        
        details = {
            '_id' : ref,
            'provider' : 'stripe',
            'what' : what,
            'account' : account,
            'amount' : amount,
            'provider_specific' : {
                'success' : True,
                'email' : email,
                'charge' : charge
            }
        }
        
        # store charge 
        db.payments.insert(details)
        return charge
    except stripe.CardError, e:
        details = {
            '_id' : ref,
            'provider' : 'stripe',
            'what' : what,
            'account' : account,
            'amount' : amount,
            'provider_specific' : {
                'success' : False,
                'error' : e.message
            }
        }
        
        # store charge 
        db.payments.insert(details)

