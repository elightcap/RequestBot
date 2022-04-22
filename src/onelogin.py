def onelogin_response(message,say):
    """respond to onelogin"""
    author = message['user']
    msg = f"""Hi <@{author}>! I see you are asking about OneLogin.
     I'm excited to inform you that we have moved to Okta as an Identity Provider. 
     Please visit https://citystoragesystems.okta.com for more info"""
    say(msg)
