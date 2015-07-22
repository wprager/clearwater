import datetime
from sqlalchemy import create_engine, Column, DateTime, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
	__tablename__ = 'users'
	
	id = Column(Integer, primary_key=True)
	username = Column(String, unique=True)
	password = Column(String) #TODO: store password hash
	
	def __init__(self, username, password):
		self.username = username
		self.password = password
	
	def __repr__(self):
		return 'User: %r' % self.username

class Measurement(Base):
	__tablename__ = 'measurements'
	
	id = Column(Integer, primary_key=True)
	timestamp = Column(DateTime, default=datetime.datetime.now)
	ph = Column(Float)

# # create tables (only need to do this once per server)
# Base.metadata.create_all(engine)
