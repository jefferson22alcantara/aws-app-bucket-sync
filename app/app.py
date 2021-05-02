import os
import sys
from flask import (
    Flask,
    url_for,
    render_template,
    request,
    redirect,
    session,
    flash,
    jsonify,
    json,
)
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a file handler
handler = logging.StreamHandler(sys.stdout)

handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# formatter = logging.Formatter(LOG_FORMATTER)
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, UserMixin, login_user

# from flask_migrate import Migrate

template_dir = os.path.abspath("./templates")
app = Flask(__name__, template_folder=template_dir, static_folder="./static")
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://docker:docker@localhost:5432/bucket_infos"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# migrate = Migrate(app, db)


class ObjectModel(db.Model):
    __tablename__ = "objects"
    id = db.Column(db.Integer, primary_key=True)
    bucket_name = db.Column(db.String())
    object_name = db.Column(db.String())
    bucket_dest_synced = db.Column(db.String())
    sync_status = db.Column(db.String())
    sync_request = db.Column(db.Boolean, default=False)

    def __init__(
        self, bucket_name, object_name, bucket_synced, sync_status, sync_request
    ):
        self.bucket_name = bucket_name
        self.object_name = object_name
        self.bucket_dest_synced = bucket_synced
        self.sync_status = sync_status
        self.sync_request = sync_request

    def __repr__(self):
        return "<id {}>".format(self.id)


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("index-2.html", title="Dashboard")


@app.route("/_list_bucket", methods=["GET"])
def list_bucket_from_db():
    bucket_name = request.args.get("bucket", 0)
    info = [
        {
            "bucket_name": "dev-s3-sensu-assets",
            "object_name": "TESTE1.txt",
            "sync_status": "Not Sync",
            "bucket_sync": " - ",
        },
        {
            "bucket_name": bucket_name,
            "object_name": "TESTE2.txt",
            "sync_status": "Not Sync",
            "bucket_sync": " - ",
        },
        {
            "bucket_name": bucket_name,
            "object_name": "Objet1",
            "sync_status": "Not Sync",
            "bucket_sync": " - ",
        },
        {
            "bucket_name": "bucket1",
            "object_name": "TESTE1.txt",
            "sync_status": "Not Sync",
            "bucket_sync": " - ",
        },
    ]
    return jsonify(info)


@app.route("/_request_sync", methods=["POST"])
def request_sync():
    ###data request return
    logger.info(type(request.data))
    infos = json.loads(request.data.decode("utf-8"))
    result = request_sync_to_db(
        infos.get("bucket_name"),
        infos.get("object_name"),
        True,
        infos.get("bucket_dest"),
    )

    return request.data


def request_sync_to_db(bucket_name, object_name, sync_request, bucket_dest):
    object_filter = ObjectModel.query.filter_by(
        object_name=object_name, bucket_name=bucket_name
    ).first()
    if object_filter is not None:
        logger.info(object_filter.id)
        logger.info("Upddate Status of request sync for True ")
        if object_filter.sync_request != True:
            object_filter.sync_request = True
            logger.info("update to dest bucket synced to bucket %s " % bucket_dest)
            object_filter.bucket_dest_synced = bucket_dest
            db.session.flush()
            db.session.commit()
        else:
            logger.info("Object already set to sync request ")

    else:
        logger.info("Object nao encontrado !!!")
    db.session.flush()
    db.session.commit()

    return {"message": f"Object  {object_name} has been requeset to sync successfully."}


if __name__ == "__main__":
    db.create_all()
    db.session.commit()
    app.run(debug=True)

