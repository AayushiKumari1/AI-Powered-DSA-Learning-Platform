import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "supersecretkey")
    SQLALCHEMY_DATABASE_URI = "sqlite:///site.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CODE_RUNNER_URL = os.environ.get("CODE_RUNNER_URL") or "https://ce.judge0.com/submissions?base64_encoded=false&wait=true"
    CODE_RUNNER_API_KEY = os.environ.get("CODE_RUNNER_API_KEY") or None
    
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')