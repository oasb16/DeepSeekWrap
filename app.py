from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_oauthlib.client import OAuth
import os
from openai import OpenAI
import json
import websocket
import logging
from datetime import datetime

# Configure Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///app.db')
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_NAME'] = 'cookie'

# Initialize DB and login manager
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# OAuth setup
oauth = OAuth(app)
google = oauth.remote_app(
    'google',
    consumer_key=os.getenv('GOOGLE_CLIENT_ID'),
    consumer_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    request_token_params={'scope': 'email profile'},
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)

class Interaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), db.ForeignKey('user.id'))
    user_input = db.Column(db.Text)
    response = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/login/callback')
def authorized():
    response = google.authorized_response()
    if response is None or response.get('access_token') is None:
        return 'Access denied'

    session['google_token'] = (response['access_token'], '')
    user_info = google.get('userinfo').data
    user = User.query.get(user_info['id'])

    if not user:
        user = User(id=user_info['id'], name=user_info['name'], email=user_info['email'])
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return redirect(url_for('index'))

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Store user interactions
def store_interaction(user_id, user_input, response_data):
    interaction = Interaction(user_id=user_id, user_input=user_input, response=response_data)
    db.session.add(interaction)
    db.session.commit()

@app.route('/query', methods=['POST'])
@login_required
def query():
    data = request.json
    user_input = data.get('input')
    service = data.get('service')
    model = data.get('model')

    if not user_input or not service or not model:
        return jsonify({'error': 'Missing input or selection'}), 400

    try:
        logger.info(f"Processing request: {user_input} | Service: {service} | Model: {model}")

        oaiclient = OpenAI()
        oaiclient.api_key = os.getenv("OPENAI_API_KEY")

        response = oaiclient.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": user_input},
            ],
            stream=False
        )

        response_data = response.choices[0].message.content
        store_interaction(current_user.id, user_input, response_data)

        return jsonify({'response': response_data})
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat_history')
@login_required
def chat_history():
    history = Interaction.query.filter_by(user_id=current_user.id).order_by(Interaction.created_at.desc()).limit(10).all()
    return jsonify([{'user_input': i.user_input, 'response': i.response} for i in history])

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
