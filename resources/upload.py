import os

from flask import request
from flask_restful import Resource
from flask_uploads import UploadNotAllowed
from http import HTTPStatus

from extensions import file_set
from utils import generate_json

class UploadResource(Resource):
    def post(self):
        try:
            # receive csv file from frontend
            file = request.files['csv_file']
            file_set.save(file, folder="local_storage", name=file.filename)
            attachmentPath = file_set.path(folder="local_storage", filename=file.filename)

            # generate json data
            json_data = generate_json(file_csv=attachmentPath, short=True)

            os.remove(attachmentPath)

            # print(json_data)

            return {
                "json_data": json_data
            }, HTTPStatus.CREATED

        except UploadNotAllowed or Exception as e:
            if UploadNotAllowed:
                return {"message": "Only CSV files"}, HTTPStatus.BAD_REQUEST
            elif e:
                return {"message": e}, HTTPStatus.BAD_REQUEST