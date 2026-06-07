# Twilio OTP SMS Setup Guide

## Step 1: Get Free Twilio Account
1. Go to https://www.twilio.com/console
2. Sign up for a free account (includes $15 free credits)
3. You'll be redirected to the Twilio Console

## Step 2: Get Your Twilio Credentials
1. On the Twilio Console Dashboard, you'll see:
   - **Account SID** (starts with "AC...")
   - **Auth Token** (long random string)
2. Copy these values

## Step 3: Get a Twilio Phone Number
1. Go to: https://www.twilio.com/console/phone-numbers/incoming
2. Click "Get Started" to get a trial phone number
3. Choose a number (free for trial)
4. Copy this phone number (format: +1XXXXXXXXXX)

## Step 4: Configure MHM Hub
1. Open `.env` file in the workspace
2. Fill in your credentials:
   ```
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=your_auth_token_here
   TWILIO_PHONE_NUMBER=+1xxxxxxxxxx
   ```

## Step 5: Add Your Phone to Verified Caller IDs (for trial)
1. Since you're on a trial account, only verified numbers can receive SMS
2. Go to: https://www.twilio.com/console/phone-numbers/verified
3. Verify your personal phone number
4. This is the number you'll use to test OTP login

## Step 6: Test OTP Login
1. Register a new user with your verified phone number
2. Go to login page
3. Switch to "OTP Login" tab
4. Enter your phone number
5. Click "Send OTP"
6. Check your phone for the OTP message
7. Enter the OTP in the "Verify OTP" form

## Pricing
- **Free Trial**: $15 free credits
- **Production**: $0.0075 per SMS (US numbers)
- Trial restrictions: Can only send to verified numbers

## Troubleshooting
- SMS not received? Check that your phone number is verified in Twilio console
- "Failed to send OTP"? Verify TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN are correct
- Check app logs for error messages from Twilio
