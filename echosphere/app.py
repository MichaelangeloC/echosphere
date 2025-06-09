from flask import Flask

# Create the Flask application instance
app = Flask(__name__)

@app.route('/')
def hello_world():
    """
    This function is tied to the root URL ('/').
    It returns a simple string to be displayed in the browser.
    """
    return '<h1>Welcome to EchoSphere!</h1><p>The server is running.</p>'

# The following block ensures this script runs only when executed directly
# (not when imported) and starts the development server.
if __name__ == '__main__':
    # Note: In a real production environment, we would use a proper WSGI server
    # instead of Flask's built-in development server.
    app.run(debug=True)

