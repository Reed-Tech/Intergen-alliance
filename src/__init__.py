from flask import Flask
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail
from .utils import *

mysql = MySQL(cursorclass=DictCursor)
limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"])
# mysql://b259eb55614b49:1e391f50@us-cdbr-east-04.cleardb.com/heroku_58802c299913439?reconnect=true
def create_app():
    app = Flask(__name__)

    config = load_config()
    app.config["SECRET_KEY"] = config["SECRET_KEY"]
    app.config["MYSQL_DATABASE_HOST"] = config["DB"]["HOST"]
    app.config["MYSQL_DATABASE_DB"] = config["DB"]["DATABASE"]
    app.config["MYSQL_DATABASE_USER"] = config["DB"]["USERNAME"]
    app.config["MYSQL_DATABASE_PASSWORD"] = config["DB"]["PASSWORD"]

    app.config["BUCKET_NAME"] = config["AWS"]["BUCKET_NAME"]
    app.config["AWS_ACCESS_KEY_ID"] = config["AWS"]["AWS_ACCESS_KEY_ID"]
    app.config["AWS_SECRET_ACCESS_KEY"] = config["AWS"]["AWS_SECRET_ACCESS_KEY"]

    mysql.init_app(app)
    limiter.init_app(app)
    # blueprint for auth routes in our app
    from .api import api
    from .main import main
    from .admin import admin

    app.register_blueprint(api)
    app.register_blueprint(main)
    app.register_blueprint(admin)

    return app
