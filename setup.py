from clearwater import db
from clearwater.config import SQLALCHEMY_DATABASE_URI
from clearwater.controllers import hash_pass
from clearwater.models import Base, User, Measurement
from sqlalchemy import create_engine

engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
Base.metadata.create_all(engine)
admin = User('admin', hash_pass('admin'), 1)
db.session.add(admin)
db.session.commit()
