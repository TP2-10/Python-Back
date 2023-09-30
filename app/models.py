import bcrypt
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password_hash = self._generate_password_hash(password)

    def _generate_password_hash(self, password):
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        return password_hash.decode('utf-8')

    def verify_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def __repr__(self):
        return f'<User {self.username}>'


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, db.ForeignKey('story.id'), nullable=False)
    url = db.Column(db.TEXT, nullable=False)  # Use TEXT instead of String

    def __init__(self, story_id, url):
        self.story_id = story_id
        self.url = url

class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=True)
    
    # Define a one-to-many relationship with images
    images = db.relationship('Image', backref='story', lazy=True)

    def __init__(self, prompt, content):
        self.prompt = prompt
        self.content = content


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, db.ForeignKey('story.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)

    options = db.relationship('Option', backref='question', lazy=True)

    def __init__(self, story_id, question_text):
        self.story_id = story_id
        self.question_text = question_text

class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)

    def __init__(self, question_id, text):
        self.question_id = question_id
        self.text = text