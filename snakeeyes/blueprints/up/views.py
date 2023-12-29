from flask import Blueprint
from sqlalchemy import text

from snakeeyes.extensions import db
from snakeeyes.initializers import redis

up = Blueprint("up", __name__, template_folder="templates", url_prefix="/up")


@up.get("/")
def index():
    return ""


@up.get("/databases")
def databases():
    redis.ping()

    with db.engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return ""
