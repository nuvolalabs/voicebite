# Environment variables to set in Railway (Project → Variables)
# Copy values from your .env — do NOT commit secrets.
#
# PUBLIC_BASE_URL   = (set after first deploy; Railway gives you a URL like https://xxx.up.railway.app)
# STRIPE_SECRET_KEY = sk_live_...
# TWILIO_ACCOUNT_SID = AC...
# TWILIO_AUTH_TOKEN  = ...
# TWILIO_FROM_NUMBER = +1...
# ADMIN_USER         = admin
# ADMIN_PASS         = <strong unique password>
# STRIPE_SUCCESS_URL = https://your-domain/order-success
# STRIPE_CANCEL_URL  = https://your-domain/order-cancel
# VAPI_SECRET        = (optional; set if you configure a secret in Vapi)
#
# After deploy, set PUBLIC_BASE_URL to the Railway URL, then redeploy.
# In vapi_assistant.json, replace {{PUBLIC_BASE_URL}} with that URL and create the assistant.
