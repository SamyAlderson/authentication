import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Project settings
    PROJECT_NAME = 'authentication'
    DESCRIPTION = 'A full-featured authentication system for handling user logins and sessions.'

    # Database settings
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Secret key for token-based authentication
    SECRET_KEY = os.getenv('SECRET_KEY')

    # Bcrypt settings
    BCRYPT_HASH_PREFIX = 12  # Default salt rounds

    # Session settings
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes

    # Testing settings
    TESTING = False

    # Debug settings
    DEBUG = False
    DEBUG_TB_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False

# Test configuration
class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.getcwd(), 'test.db')
    SECRET_KEY = 'test_key'