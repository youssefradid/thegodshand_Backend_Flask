import os 
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or "not-a-chance"
    # SQLALCHEMY config variables
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '').replace(
        'postgres://', 'postgresql://') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Config variables for email(both errors & auth. emails)
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 25)
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") is not None
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    ADMINS = os.environ.get("ADMINS")
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    # Config variable for pagination
    POSTS_PER_PAGE = 20
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER")
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg','gif'}
    MAX_CONTENT_LENGTH = 500 * 1024 #500 KB

config = Config()