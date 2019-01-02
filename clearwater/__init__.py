from flask import Flask
from flask_heroku import Heroku
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_pyfile('config.py')
heroku = Heroku(app)
db = SQLAlchemy(app)