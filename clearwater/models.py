from clearwater import app, db
import datetime
from flask.ext.login import UserMixin
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy import create_engine, Column, DateTime, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
login_serializer = URLSafeTimedSerializer(app.secret_key)
s = db.session

class User(Base, UserMixin):
	__tablename__ = 'users'
	
	id = Column(Integer, primary_key=True)
	username = Column(String, unique=True)
	password = Column(String)
	
	def __init__(self, username, password):
		self.username = username
		self.password = password
	
	def get_auth_token(self):
		data = [self.username, self.password]
		return login_serializer.dumps(data)
		# return make_secure_token(self.username, self.password)
	
	@staticmethod
	def get(data):
		if type(data) == unicode: # get by id
			return s.query(User).filter(User.id.in_([data])).first()
		elif type(data) == str: # get by username
			return s.query(User).filter(User.username.in_([data])).first()
	
	@staticmethod
	def getAll():
		return s.query(User).all()
	
	@staticmethod
	def create(user):
		s.add(user)
		s.commit()
	
	@staticmethod
	def delete(user):
		s.delete(user)
		s.commit()
	
	def __repr__(self):
		return 'User: %r' % self.username

class Measurement(Base):
	__tablename__ = 'measurements'
	
	id = Column(Integer, primary_key=True)
	timestamp = Column(DateTime, default=datetime.datetime.now)
	ph = Column(Float)

# # create tables (only need to do this once per server)
# Base.metadata.create_all(engine)
