import os
from dotenv import load_dotenv

load_dotenv()

class Config(object):
    DEBUG = False
    SECRET_KEY = os.urandom(24)
    UPLOADED_FILES_DEST = 'static'
    CORS_SUPPORTS_CREDENTIALS = True
    CORS_RESOURCES = r'/*'
    CORS_ORIGINS = [
        os.environ['FRONTEND_URL'],
        os.environ['FRONTEND_URL_DEV']
    ]
    
class DevelopmentConfig(Config):
    DEBUG = True