from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_oauthlib.client import OAuth
import os
from openai import OpenAI
import json
import websocket


# Configure Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')

# Configure PostgreSQL database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL').replace("postgres://", "postgresql://")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Configure OAuth for Google SSO
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

# User model
class User(db.Model, UserMixin):
    __tablename__ = "users"
    user_id = db.Column(db.String(255), primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255))
    created_at = db.Column(db.TIMESTAMP, default=db.func.now())

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
        return "Access denied."

    session['google_token'] = (response['access_token'], '')
    user_info = google.get('userinfo')
    user_data = user_info.data

    user_id = user_data.get('id')
    email = user_data.get('email')
    name = user_data.get('name')

    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        user = User(user_id=user_id, email=email, name=name)
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

@app.route('/query', methods=['POST'])
@login_required
def query():
    data = request.json
    user_input = data.get('input')
    selected_service = data.get('service')
    selected_model = data.get('model')

    if not user_input or not selected_service or not selected_model:
        return jsonify({'error': 'Missing input or selection'}), 400

    try:
        if selected_service == 'deepseek':
            client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"))
            response = client.chat.completions.create(
                model=selected_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant"},
                    {"role": "user", "content": user_input},
                ],
                stream=False
            )
        elif selected_service == 'openai':
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model=selected_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant"},
                    {"role": "user", "content": user_input},
                ],
                stream=False
            )
        else:
            return jsonify({'error': 'Invalid service selected'}), 400

        response_data = response.choices[0].message.content
        return jsonify(response_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)


import logging
from datetime import datetime
logger = logging.getLogger(__name__)

def create_user(user_data):
    # Code to create user
    logger.info(f"New user created: {user_data['username']}")

# def log_user_stats():
#     total_users = get_total_user_count()  # Implement this function
#     logger.info(f"{datetime.now()}: Total users: {total_users}")

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

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
        oaiclient = OpenAI()
        oaiclient.api_key = os.getenv("OPENAI_API_KEY")
        # example requires websocket-client library:
        # pip install websocket-client


        OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

        url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"
        headers = [
            "Authorization: Bearer " + OPENAI_API_KEY,
            "OpenAI-Beta: realtime=v1"
        ]
        message=[{"role": "system", "content": "You are a helpful assistant"},{"role": "user", "content": user_input}]
        print("message : " + str(message))
        print("headers : " + str(headers))
        print("url : " + str(url))

        # # To send a client event, serialize a dictionary to JSON
        # # of the proper event type
        # def on_open(ws):
        #     print("Connected to server.")
            
        #     event = {
        #         "type": "response.create",
        #         "response": {
        #             "modalities": ["text"],
        #             "instructions": "Please assist the user."
        #         }
        #     }
        #     ws.send(json.dumps(event))

        # # Receiving messages will require parsing message payloads
        # # from JSON
        # def on_message(ws, message):
        #     data = json.loads(message)
        #     print("Received event:", json.dumps(data, indent=2))

        # ws = websocket.WebSocketApp(
        #     url,
        #     header=headers,
        #     on_open=on_open,
        #     on_message=on_message,
        # )

        # ws.run_forever()

        response = oaiclient.chat.completions.create(
            model=model,
            messages=message,
            stream=False
        )

        response_data = response.choices[0].message.content
        store_interaction(current_user.id, user_input, response_data)
        return jsonify({'response': response_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat_history')
@login_required
def chat_history():
    history = Interaction.query.filter_by(user_id=current_user.id).order_by(Interaction.id.desc()).limit(10).all()
    return jsonify([{'user_input': i.user_input, 'response': i.response} for i in history])

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
