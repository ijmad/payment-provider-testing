#!/usr/bin/env sh

cat > config.sh << EOF
export PYTHONPATH="payments"

export FLASK_SECRET="<your secret>"

export MONGO_HOST="localhost"
export MONGO_PORT="27017"

export GOCARDLESS_USER="<your client key here>"
export GOCARDLESS_PASS="<your secret here>"

export STRIPE_KEY="<your key here>"

export PAYPAL_USER="<your user here>"
export PAYPAL_PASS="<your pass here>"

export EMAIL_USER="<your user here>"
export EMAIL_PASS="<your pass here>"
EOF
