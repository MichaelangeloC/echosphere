import uuid
from flask import Flask, jsonify, request, render_template_string
from echosphere import config
from echosphere.models import db, Post

# --- App Initialization ---
app = Flask(__name__)
# Load config from the config.py file
app.config.from_pyfile('config.py')
# Initialize the database with our app
db.init_app(app)

# --- One-time Database Setup ---
with app.app_context():
    # This will create the database file and tables if they don't exist
    db.create_all()

# --- Core Routes ---
@app.route('/')
def hello_world():
    """ Main landing page. """
    return '<h1>Welcome to EchoSphere!</h1><p>The server can now create and display posts.</p>'

# --- Actor and WebFinger Routes (from previous phase) ---
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
    else:
        return "User not found", 404

@app.route('/actor')
def actor():
    """ The Actor profile for our server. """
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

# --- NEW: Outbox and Post Creation Routes ---
@app.route('/outbox')
def outbox():
    """ The Outbox, which lists all posts created by our actor. """
    # Fetch all posts from the database, newest first
    posts_from_db = Post.query.order_by(Post.created_at.desc()).all()
    
    # Format the posts into an ActivityPub collection
    ordered_collection = {
        "@context": "https://www.w3.org/ns/activitystreams",
        "id": f"http://{app.config['DOMAIN']}/outbox",
        "type": "OrderedCollection",
        "totalItems": len(posts_from_db),
        "orderedItems": [
            {
                "id": post.uri,
                "type": "Create",
                "actor": f"http://{app.config['DOMAIN']}/actor",
                "published": post.created_at.isoformat(),
                "object": {
                    "id": post.uri,
                    "type": "Note",
                    "published": post.created_at.isoformat(),
                    "attributedTo": f"http://{app.config['DOMAIN']}/actor",
                    "content": post.content,
                    "to": ["https://www.w3.org/ns/activitystreams#Public"]
                }
            } for post in posts_from_db
        ]
    }
    return jsonify(ordered_collection)

@app.route('/create-post', methods=['GET', 'POST'])
def create_post():
    """ A simple internal form to create a new post. THIS IS NOT for users. """
    if request.method == 'POST':
        content = request.form['content']
        if content:
            # Create a new Post object and save it to the database
            new_post = Post(
                uri=f"http://{app.config['DOMAIN']}/posts/{uuid.uuid4()}",
                content=content
            )
            db.session.add(new_post)
            db.session.commit()
            return 'Post created! <a href="/create-post">Create another</a> or <a href="/outbox">View Outbox</a>'

    # Display the form to create a post
    return render_template_string('''
        <h1>Create New Post (Internal Tool)</h1>
        <form method="post">
            <textarea name="content" rows="10" cols="50"></textarea>
            <br>
            <input type="submit" value="Create Post">
        </form>
    ''')

# --- Main run block ---
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
    
