import os
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


class BucketModel(db.Model):
    __tablename__ = "buckets"
    id = db.Column(db.Integer, primary_key=True)
    bucket = db.Column(db.String())
    obj = db.Column(db.String())
    bucket_synced = db.Column(db.String())
    sync_status = db.Column(db.String())
    sync_request = db.Column(db.Boolean, default=False)

    def __init__(self, bucket, obj, bucket_synced, sync_status, sync_request):
        self.bucket = bucket
        self.obj = obj
        self.bucket_synced = bucket_synced
        self.sync_status = sync_status
        self.sync_request = sync_request

    def __repr__(self):
        return "<id {}>".format(self.id)


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("index-2.html", title="Dashboard")


@app.route("/_list_bucket", methods=["GET"])
def list_bucket_from_db():
    bucket_name_source = request.args.get("bucket", 0)
    info = [
        {
            "bucket": bucket_name_source,
            "obj": "Obj1",
            "sync_status": "Not Sync",
            "bucket_sync": " - ",
        },
        {
            "bucket": bucket_name_source,
            "obj": "Obj2",
            "sync_status": "Not Sync",
            "bucket_sync": " - ",
        },
        {
            "bucket": bucket_name_source,
            "obj": "Obj3",
            "sync_status": "Not Sync",
            "bucket_sync": " - ",
        },
    ]
    return jsonify(info)


@app.route("/_request_sync", methods=["POST"])
def request_sync():
    ###data request return
    print(type(request.data))
    infos = json.loads(request.data.decode("utf-8"))
    result = insert_object_info_on_pg_from_bucket(
        infos.get("bucket"), infos.get("obj"), "-", "Not sync", True
    )

    return request.data


def insert_object_info_on_pg_from_bucket(
    bucket, obj, bucket_synced, sync_status, sync_request
):
    new_object = BucketModel(
        bucket=bucket,
        obj=obj,
        bucket_synced=bucket_synced,
        sync_status=sync_status,
        sync_request=sync_request,
    )
    db.session.add(new_object)
    db.session.commit()
    return {"message": f"Object  {new_object.obj} has been created successfully."}


if __name__ == "__main__":
    db.create_all()
    db.session.commit()
    app.run(debug=True)

