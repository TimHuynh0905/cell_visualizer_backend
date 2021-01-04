import os
from flask import Flask
from flask_restful import Api
from flask_uploads import configure_uploads
from dotenv import load_dotenv

from resources.upload import UploadResource
from extensions import cors, file_set
from config import Config, DevelopmentConfig

load_dotenv()

def create_app():
    app = Flask(__name__)

    if os.environ['ENV'] == 'dev':
        app.config.from_object(DevelopmentConfig)
    else:
        app.config.from_object(Config)
    
    register_extensions(app)
    register_resources(app)
    
    return app

def register_extensions(app):
    cors.init_app(app)
    configure_uploads(app, file_set)

def register_resources(app):
    api = Api(app)
    api.add_resource(UploadResource, '/upload_csv')


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)