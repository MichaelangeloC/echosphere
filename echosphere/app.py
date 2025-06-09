from flask import Flask, jsonify, request
from echosphere import config # Import our new config file

# Create the Flask application instance
app = Flask(__name__)

@app.route('/')
def hello_world():
    """
    This function is tied to the root URL ('/').
    It returns a simple string to be displayed in the browser.
    """
    return '<h1>Welcome to EchoSphere!</h1><p>The server is running and now has a basic identity.</p>'

@app.route('/.well-known/webfinger')
def webfinger():
    """
    The WebFinger endpoint.
    It provides machine-readable information about a user on our server.
    Example request: /.well-known/webfinger?resource=acct:server@localhost:5000
    """
    resource = request.args.get('resource')
    if not resource or not resource.startswith('acct:'):
        return "Bad Request: 'resource' parameter is required and must start with 'acct:'", 400

    # We are parsing the "acct:username@domain" string
    account = resource.split(':')[1]
    username, domain = account.split('@')

    # For now, we only respond to requests for our server's main actor
    if username == config.ACTOR_USERNAME and domain == config.DOMAIN:
        # If it's our user, return the JRD (JSON Resource Descriptor)
        return jsonify({
            "subject": f"acct:{config.ACTOR_USERNAME}@{config.DOMAIN}",
            "links": [
                {
                    "rel": "self",
                    "type": "application/activity+json",
                    "href": f"http://{config.DOMAIN}/actor" # We will create this URL in the next phase
                }
            ]
        })
    else:
        # If the user is not found, return a 404 Not Found error
        return "User not found", 404


# The following block ensures this script runs only when executed directly
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

