import flask, flask_restful, flask_uploads, flask_cors, boto3, http, os, json, simplejson, dotenv
from pval-plunker import *

dotenv.load_dotenv()

attachmentSet = flask_uploads.UploadSet("files", ("csv",))
s3Bucket = boto3.resource (
    "s3",
    region_name=os.environ.get("AWS_REGION"),
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_KEY")
)

class UploadResource(flask_restful.Resource):
    def post(self):
        if flask.request.method == 'OPTIONS':
            response = flask.make_response()
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add('Access-Control-Allow-Headers', "*")
            response.headers.add('Access-Control-Allow-Methods', "*")
            return response
        elif flask.request.method == 'POST' and "csvData" in flask.request.files:
            try:
                # receive csv file from frontend
                file = flask.request.files['csvData']
                fileName = "plunker_inputs_" + file.filename.split(".")[0] + ".json"
                
                # generate json data

                with open("static/local_storage" + fileName, 'w') as file:
                    simplejson.dump(ld, file, ignore_nan=True) 

                
                # upload json file to s3 bucket and send it back to frontend
                s3Bucket.Bucket(os.environ.get("PROJECT_BUCKET")).upload_file(
                    Filename = f"static/local_storage/{fileName}",
                    Key = f"filesCollection/{fileName}",
                    ExtraArgs = {'ACL': 'public-read'}
                )
                contentObject = s3Bucket.Object(os.environ.get("PROJECT_BUCKET"), f"{fileName}")
                jsonContent = json.loads(contentObject.get()['Body'].read().decode('utf-8'))
                return jsonContent["Details"], http.HTTPStatus.ACCEPTED

            except flask_uploads.UploadNotAllowed or Exception as e:
                if flask_uploads.UploadNotAllowed: return {"message":"Only CSV files"}, http.HTTP.BAD_REQUEST
                elif e: return {"message": e}, http.HTTPStatus.BAD_REQUEST


def create_app():
    app = flask.Flask(__name__)
    flask_cors.CORS(app, expose_headers='Authorization')
    app.config['UPLOADED_FILES_DEST'] = 'static/local_storage'
    flask_uploads.configure_uploads(app, attachmentSet)
    @app.route('/')
    def index():
        return {'message': 'root api'}
    register_resources(app)
    return app

def register_resources(app):
    api = flask_restful.Api(app)
    api.add_resources(UploadResource, '/upload_csv')
    

if __name__ == '__main__':
    app = create_app()
    app.run(debug = True)