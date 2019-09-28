from paperbroker import PaperBroker
from paperbroker.orders import Order


# Creating a PaperBroker defaults to:
# - uses the local filesystem temp folder to store acounts
# - quotes from Google Finance (equities only)
# - estimates all transaction prices at the midpoint
# - you can change any of these by writing your own adapters, see paperbroker/adapters
broker = PaperBroker()

# Create an account so we can buy stuff
account = broker.open_account()
account.cash = 100000 # give ourselves some cash!!

# This is how we get basic quotes
# We can get any quotes supported by GoogleFinance
quote = broker.get_quote('GOOG')
print(quote.price)
# >> 943.83

# Get the expiration dates that GoogleFinance has for GOOG
expiration_dates = broker.get_expiration_dates('GOOG')
print(expiration_dates)
# >> ['2018-01-19']