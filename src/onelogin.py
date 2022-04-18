def onelogin_response(ack,body,say):
    """respond to onelogin"""
    ack()
    author = body['user']['name']
    msg = """Hi {author}! I see you are asking about OneLogin.
     I'm excited to inform you that we have moved to Okta as an Identity Provider. 
     Please visit https://citystoragesystems.okta.com for more info"""
    say(msg)
    