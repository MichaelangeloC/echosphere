import uuid
import json
from flask import Flask, jsonify, request, render_template_string
from echosphere import config
from echosphere.models import db, Post

# --- App Initialization ---
app = Flask(__name__)
app.config.from_pyfile('config.py')
db.init_app(app)

# --- One-time Database Setup ---
with app.app_context():
    db.create_all()

# --- Core Routes ---
@app.route('/')
def hello_world():
    return '<h1>Welcome to EchoSphere!</h1><p>MVP Complete: The server can now send and receive federated messages.</p>'

# --- Actor and WebFinger Routes ---
@app.route('/.well-known/webfinger')
def webfinger():
    resource = request.args.get('resource')
    if not resource or not resource.startswith('acct:'):
        return "Bad Request", 400
    account = resource.split(':')[1]
    username, domain = account.split('@')
    if username == app.config['ACTOR_USERNAME'] and domain == app.config['DOMAIN']:
        return jsonify({
            "subject": f"acct:{app.config['ACTOR_USERNAME']}@{app.config['DOMAIN']}",
            "links": [{"rel": "self", "type": "application/activity+json", "href": f"http://{app.config['DOMAIN']}/actor"}]
        })
    return "User not found", 404

@app.route('/actor')
def actor():
    return jsonify({
        "@context": ["https://www.w3.org/ns/activitystreams", "https://w3id.org/security/v1"],
        "id": f"http://{app.config['DOMAIN']}/actor",
        "type": "Application",
        "preferredUsername": app.config['ACTOR_USERNAME'],
        "name": "EchoSphere Server",
        "summary": "This is the main server actor for the EchoSphere application.",
        "inbox": f"http://{app.config['DOMAIN']}/inbox",
        "outbox": f"http://{app.config['DOMAIN']}/outbox",
    })

# --- Outbox and Post Creation Routes ---
@app.route('/outbox')
def outbox():
    posts_from_db = Post.query.order_by(Post.created_at.desc()).all()
    ordered_collection = {
        "@context": "https://www.w3.org/ns/activitystreams",
        "id": f"http://{app.config['DOMAIN']}/outbox",
        "type": "OrderedCollection",
        "totalItems": len(posts_from_db),
        "orderedItems": [
            {"id": post.uri, "type": "Create", "actor": f"http://{app.config['DOMAIN']}/actor", "published": post.created_at.isoformat(),
             "object": {"id": post.uri, "type": "Note", "published": post.created_at.isoformat(), "attributedTo": f"http://{app.config['DOMAIN']}/actor",
                        "content": post.content, "to": ["https://www.w3.org/ns/activitystreams#Public"]}} for post in posts_from_db
        ]
    }
    return jsonify(ordered_collection)

@app.route('/create-post', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        content = request.form['content']
        if content:
            new_post = Post(uri=f"http://{app.config['DOMAIN']}/posts/{uuid.uuid4()}", content=content)
            db.session.add(new_post)
            db.session.commit()
            return 'Post created! <a href="/create-post">Create another</a> or <a href="/outbox">View Outbox</a>'
    return render_template_string('''<h1>Create New Post (Internal Tool)</h1><form method="post"><textarea name="content" rows="10" cols="50"></textarea><br><input type="submit" value="Create Post"></form>''')

# --- NEW: Inbox Route for Federation ---
@app.route('/inbox', methods=['POST'])
def inbox():
    """
    The Inbox, where we receive activities from other servers.
    """
    # Get the raw request body
    activity = request.get_json()

    # In a real app, we would verify the HTTP Signature here. We are skipping this for the MVP.

    # Print the activity to the console for debugging. In a real app, this would be a logger.
    print("--- INBOX: ACTIVITY RECEIVED ---")
    print(json.dumps(activity, indent=2))
    print("--------------------------------")

    # For now, we are just acknowledging the activity. We are not processing it further (e.g., saving it).
    # We will simply check if it's a "Create" activity for a "Note" and print a success message.
    if activity.get('type') == 'Create':
        obj = activity.get('object', {})
        if obj.get('type') == 'Note':
            author = activity.get('actor')
            content = obj.get('content', '[No Content]')
            print(f"Received a new Note from: {author}")
            print(f"Content: {content[:100]}...")

    # According to the ActivityPub spec, we should return a 202 Accepted status
    # to indicate that we have received the request and will process it.
    return "Accepted", 202

# --- Main run block ---
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
