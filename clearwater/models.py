from clearwater import app, db
import constants
import datetime
from flask.ext.login import UserMixin
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
login_serializer = URLSafeTimedSerializer(app.secret_key)
s = db.session

class User(Base, UserMixin):
	__tablename__ = 'users'
	
	id = Column(Integer, primary_key=True)
	username = Column(String, unique=True)
	password = Column(String)
	status = Column(Integer, default=constants.USER)
	measurements = db.relationship('Measurement', backref=db.backref('user', lazy='joined'), lazy='dynamic')
	
	def __init__(self, username, password, status=constants.USER):
		self.username = username
		self.password = password
		self.status = status
		self.measurements = []
	
	def get_auth_token(self):
		data = [self.username, self.password]
		return login_serializer.dumps(data)
		# return make_secure_token(self.username, self.password)
	
	def isAdmin(self):
		return self.status == constants.ADMIN;
	
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
		return 'User: {0}'.format(self.username)

class Measurement(Base):
	__tablename__ = 'measurements'
	
	id = Column(Integer, primary_key=True)
	timestamp = Column(DateTime, default=datetime.datetime.now, unique=True)
	ph = Column(Float)
	dissolved_oxygen = Column(Float)
	electro_conductivity = Column(Float)
	temperature = Column(Float)
	user_id = Column(Integer, ForeignKey('users.id'))
	
	def __init__(self, user_id, timestamp, ph, do, ec, temp):
		self.user_id = user_id
		self.timestamp = timestamp
		self.ph = ph
		self.dissolved_oxygen = do
		self.electro_conductivity = ec
		self.temperature = temp
	
	@staticmethod
	def get(data):
		if type(data) == unicode: # get by id
			return s.query(Measurement).filter(Measurement.id.in_([data])).first()
		elif type(data) == datetime.datetime: # get by timestamp
			return s.query(Measurement).filter(Measurement.timestamp.in_([data])).first()
	
	@staticmethod
	def getAll():
		return s.query(Measurement).all()
	
	@staticmethod
	def create(measurement):
		s.add(measurement)
		s.commit()
	
	@staticmethod
	def delete(measurement):
		s.delete(measurement)
		s.commit()
	
	def __repr__(self):
		return 'Measurement: Time: {0}, pH: {1}, DO: {2}, EC: {3}, TEMP: {4}'.format(self.timestamp, self.ph, self.do, self.ec, self.temp)
