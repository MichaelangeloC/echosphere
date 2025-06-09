# --- Configuration for EchoSphere ---

# DOMAIN: This is the most important setting.
# It's the public-facing domain name of your server.
# For now, we will use 'localhost:5000' for local testing.
# When you deploy this for real, you would change this to "yourdomain.com".
DOMAIN = "localhost:5000"

# ACTOR_USERNAME: This will be the default "user" for our server instance.
# Think of it like the main admin or mascot account.
ACTOR_USERNAME = "server"

# --- Configuration for EchoSphere ---

# DOMAIN: The public-facing domain name of your server.
DOMAIN = "localhost:5000"

# ACTOR_USERNAME: The default "user" for our server instance.
ACTOR_USERNAME = "server"

# --- Database Configuration ---
# This tells our app where to store the database file.
# 'sqlite:///project.db' means the file will be named 'project.db'
# and located in a special 'instance' folder that Flask creates.
SQLALCHEMY_DATABASE_URI = 'sqlite:///project.db'
