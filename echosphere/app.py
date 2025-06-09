from flask import Flask, jsonify, request
from echosphere import config # Import our config file

# Create the Flask application instance
app = Flask(__name__)

@app.route('/')
def hello_world():
    """
    This function is tied to the root URL ('/').
    It returns a simple string to be displayed in the browser.
    """
    return '<h1>Welcome to EchoSphere!</h1><p>The server is running and now has a full Actor profile.</p>'

@app.route('/.well-known/webfinger')
def webfinger():
    """
    The WebFinger endpoint.
    Provides machine-readable info about a user on our server.
    """
    resource = request.args.get('resource')
    if not resource or not resource.startswith('acct:'):
        return "Bad Request: 'resource' parameter is required and must start with 'acct:'", 400

    account = resource.split(':')[1]
    username, domain = account.split('@')

    if username == config.ACTOR_USERNAME and domain == config.DOMAIN:
        return jsonify({
            "subject": f"acct:{config.ACTOR_USERNAME}@{config.DOMAIN}",
            "links": [
                {
                    "rel": "self",
                    "type": "application/activity+json",
                    "href": f"http://{config.DOMAIN}/actor"
                }
            ]
        })
    else:
        return "User not found", 404

@app.route('/actor')
def actor():
    """
    The Actor endpoint.
    This provides a machine-readable JSON profile of our server's user.
    """
    # This is the JSON data that other Fediverse servers will read.
    # It describes our 'server' user.
    actor_profile = {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://w3id.org/security/v1"
        ],
        "id": f"http://{config.DOMAIN}/actor",
        "type": "Application", # We are an application, not a person
        "preferredUsername": config.ACTOR_USERNAME,
        "name": "EchoSphere Server",
        "summary": "This is the main server actor for the EchoSphere application. We share long-form text and links.",
        
        # These next URLs are very important. We will build them in future phases.
        "inbox": f"http://{config.DOMAIN}/inbox",  # Where we receive messages
        "outbox": f"http://{config.DOMAIN}/outbox", # Where we post our content
    }
    return jsonify(actor_profile)


# The following block ensures this script runs only when executed directly
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

