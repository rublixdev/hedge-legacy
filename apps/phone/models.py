import twilio
import random
from django.conf import settings

from twilio.rest import Client

RBLX_NUMBER = "+15878015794"

# Enable to print SMS code to terminal instead of sending actual SMS
TESTING = False

def send_phone_verification_code(user):

	SMS_code = random.randint(100000, 999999)
		
	user.profile.SMS_activation_code = SMS_code
	user.profile.save()
	user_number = "+"+str(user.profile.phone_number)

	if TESTING==True:
		print ("The code "+str(SMS_code)+" was sent to "+str(user_number))
	else:
		client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
		client.messages.create(to = user_number, from_ = RBLX_NUMBER, body = str(SMS_code))

