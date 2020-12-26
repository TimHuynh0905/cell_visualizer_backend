from flask_cors import CORS
from flask_uploads import UploadSet

cors = CORS()
file_set = UploadSet("files", ("csv",))