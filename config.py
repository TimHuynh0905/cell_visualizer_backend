import os

class Config(object):
    DEBUG = False
    SECRET_KEY = os.urandom(24)
    UPLOADED_FILES_DEST = 'static'

class DevelopmentConfig(Config):
    DEBUG = True
    CORS_SUPPORTS_CREDENTIALS = True
    CORS_RESOURCES = r'/*'
    CORS_ORIGINS = 'http://localhost:4200'