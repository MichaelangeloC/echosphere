from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import datetime

# This creates the database object, but doesn't attach it to our app yet.
db = SQLAlchemy()

class Post(db.Model):
    """Represents a single post in our database."""
    id = db.Column(db.Integer, primary_key=True)
    uri = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f'<Post {self.id}>'
