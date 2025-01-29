from flask import Flask, render_template, request, jsonify
import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_oauthlib.client import OAuth
from openai import OpenAI

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')
app.config['SESSION_COOKIE_NAME'] = 'your_session_cookie_name'

login_manager = LoginManager()
login_manager.init_app(app)

oauth = OAuth(app)
google = oauth.remote_app(
    'google',
    consumer_key=os.getenv('GOOGLE_CLIENT_ID'),
    consumer_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    request_token_params={
        'scope': 'email profile',
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)


DEEPSEEK_API_URL = 'https://api.deepseek.com'  # Replace with the actual DeepSeek API endpoint

@app.route('/')
def index():
    return render_template('index.html')

class User(UserMixin):
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/login/callback')
def authorized():
    response = google.authorized_response()
    if response is None or response.get('access_token') is None:
        return 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )

    session['google_token'] = (response['access_token'], '')
    user_info = google.get('userinfo')
    user_data = user_info.data
    user = User(id=user_data['id'], name=user_data['name'], email=user_data['email'])
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
            # Implement DeepSeek API call
            try:
                oaiclient = OpenAI()
                oaiclient.api_key = os.getenv("OPENAI_API_KEY")
                response = oaiclient.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant"},
                        {"role": "user", "content": user_input},
                    ],
                    stream=False
                )
                response_data = response.choices[0].message.content
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        elif selected_service == 'openai':
            # Implement OpenAI API call
            try:
                oaiclient = OpenAI()
                oaiclient.api_key = os.getenv("OPENAI_API_KEY")
                response = oaiclient.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant"},
                        {"role": "user", "content": user_input},
                    ],
                    stream=False
                )
                response_data = response.choices[0].message.content
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'error': 'Invalid service selected'}), 400

        # Store the user query and response



        store_user_interaction(current_user.id, user_input, response_data)
        return jsonify(response_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
