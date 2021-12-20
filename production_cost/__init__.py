import os
import sys

sys.path.append(os.getcwd())

import logging
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from production_cost.config import Config
from flask import Flask

app = Flask(__name__)
client = app.test_client()

engine = create_engine(
    f"postgresql://{Config.USER}:{Config.PASS}@{Config.HOST}:{int(Config.PORT)}/{Config.NAME}"
)
session_db = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
Base = declarative_base()
Base.query = session_db.query_property()


def setup_logger():
    try:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s")
        file_handler = logging.FileHandler("log/api.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        return logger
    except FileNotFoundError:
        os.makedirs("log")
        return setup_logger()


logger = setup_logger()


@app.teardown_appcontext
def shutdown_session(exception=None):
    session_db.remove()


from production_cost.amp_cost.cost_view import costs

app.register_blueprint(costs)
