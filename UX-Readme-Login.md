<img src="https://i.imgur.com/dHQKtGy.png" alt="Drawing" style="width: 160px;"/>

## Welcome to the Hedge UX
**The user interface documents depend on the CSS, JS within this folder.**

#### Following HTML files are currently available for the login architecture:
	login.html >> Log in Screen
	forgotpw.html >> Forgot Password Sceen
	register.html >> Registration Screen

#### Following CSS files are currently available for the login architecture:

Files are located in:

	assets/stylesheets

#### OAuth Login
We are looking to use Facebook and Google OAuth2 (read-only) to get a users email address to sign-in 
or register a new account. We will use the JSON output to pre-populate the registration form when a user
chooses to login or sign up using OAuth2.

#### Registration Page
The following data requires collection:

	Sign Up Date
	IP Address
	Username
	Password
	Email Address
	Phone Number
	Country
	Wallet Address
	Confirm Terms Checkbox Status

#### Javascript Calendar Chooser for Date of Birth

The settings can be altered for the DOB in:

	assets/javascript/date-range-picker-settings.js 

#### SMS Authentication

We want to use Twilio Authy API to send an SMS verification then do a 
callback to make sure the number is valid. This will help us prevent
spam accounts from being created.

[See API for Twilio Here](https://www.twilio.com/docs/api/authy/authy-phone-verification-api#production-api-locations)

#### Mailchip Integration

We want to use Mailchimp API to push registration data into a new mailing list.

[See API for Mailchimp Here](http://developer.mailchimp.com/documentation/mailchimp/guides/get-started-with-mailchimp-api-3/)

#### Database Table Example Format

| Date       | IP        | Full Name        | Username      | Password (Hash)				     | Email Address   | Phone Number  | Country | Wallet Address | DOB        | Terms |
|------------|-----------|------------------|---------------|------------------------------------|-----------------|---------------|---------|----------------|------------|-------|
| 11/21/2017 | 127.0.0.1 | Vitalik Burito   | rublixuser    | 5d41402abc4b2a76b9719d911017c592   | info@rublix.io  | 15873789654   | Canada  | 0x000000000000 | 02/15/2017 | Yes   |

#### Form Specs

    Date Stamp Format: 11/21/2017
    IP: IPv4 or IPv6 value
    Full Name Format: Min 6 Char including space
    Password: Min 9 Char
    Email: Min 7 Char / Must Contain @ .
    Phone Number: Min 12 Char including -
    Wallet Address: 
    DOB: Verify 18 years of age