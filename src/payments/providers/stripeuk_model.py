import stripe
from payments.persistence import client
from payments.config import stripe_key

db = client.payments



stripe.api_key = stripe_key
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
            'success' : True,
            'method' : 'card',
            'provider' : 'stripe',
            'account' : account,
            'amount' : amount,
            'what' : what,
            'result' : charge,
            'email' : email
        }
        
        # store charge 
        db.payments.insert(details)
        return charge
    except stripe.CardError, e:
        details = {
            '_id' : ref,
            'success' : False,
            'method' : 'card',
            'provider' : 'stripe',
            'account' : account,
            'amount' : amount,
            'what' : what,
            'message' : e.message
        }
        
        # store charge 
        db.payments.insert(details)

