# DeepSeek Proxy Gateway

## Overview
DeepSeek Proxy Gateway is a web-based AI chat interface allowing users to interact with AI models from DeepSeek and OpenAI. Users can log in using Google SSO, select a service and model, and engage in a chat-like experience with stored interaction history.

## Features
- **Google SSO Authentication**: Users log in securely via Google.
- **AI Model Selection**: Choose between DeepSeek and OpenAI services.
- **Real-time Query Processing**: Supports OpenAI GPT models and DeepSeek.
- **Chat History**: Stores past conversations per user.
- **Heroku Deployment**: Optimized for deployment on Heroku.

## Tech Stack
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Flask, Flask-Login, Flask-OAuthlib
- **Database**: PostgreSQL (Heroku Postgres)
- **APIs**: OpenAI API, DeepSeek API

## Setup & Installation

### Prerequisites
- Python 3.8+
- PostgreSQL database
- Heroku CLI (if deploying to Heroku)
- Google OAuth Client Credentials

### Clone Repository
```sh
git clone https://github.com/your-repo/deepseek-proxy.git
cd deepseek-proxy
```

### Install Dependencies
Create a virtual environment and install required packages:
```sh
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

### Configure Environment Variables
Create a `.env` file and add the following:
```env
SECRET_KEY='your_secret_key'
DATABASE_URL='your_database_url'
GOOGLE_CLIENT_ID='your_google_client_id'
GOOGLE_CLIENT_SECRET='your_google_client_secret'
OPENAI_API_KEY='your_openai_api_key'
```

### Database Setup
If using Flask-Migrate, initialize the database:
```sh
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```
Otherwise, create tables manually:
```sh
heroku run python
>>> from app import db, app
>>> with app.app_context():
>>>     db.create_all()
>>>     print("✅ Database tables created successfully!")
```

### Run Locally
```sh
flask run
```
Application will be available at `http://127.0.0.1:5000`

## Deploy to Heroku
### 1. Log in to Heroku & Create App
```sh
heroku login
heroku create deepseek-wrap
```

### 2. Add PostgreSQL Add-on
```sh
heroku addons:create heroku-postgresql:essential-0
```

### 3. Set Environment Variables
```sh
heroku config:set SECRET_KEY='your_secret_key'
heroku config:set DATABASE_URL='your_database_url'
heroku config:set GOOGLE_CLIENT_ID='your_google_client_id'
heroku config:set GOOGLE_CLIENT_SECRET='your_google_client_secret'
heroku config:set OPENAI_API_KEY='your_openai_api_key'
```

### 4. Deploy Code
```sh
git push heroku main
heroku restart
```

## Troubleshooting
### Check Logs
```sh
heroku logs --tail
```
### Debug PostgreSQL Issues
```sh
heroku pg:psql -c "\d interaction"
```
### Common Fixes
- **Database migration issues**: Run `flask db migrate` and `flask db upgrade`.
- **App crash due to missing columns**: Manually alter the table or delete it and recreate.
- **Check API Keys**: Ensure OpenAI and Google credentials are correctly set.

## License
MIT License

## Contributors
- **Omkar Sawant Bhosle** (@omkarsbdev)

