from flask import Flask
from flask.ext.heroku import Heroku
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
# app.config.from_pyfile('config.py')
heroku = Heroku(app)
db = SQLAlchemy(app)