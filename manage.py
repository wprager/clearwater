from clearwater import app, db
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
	manager.run()


''' Commands:
Local:
	python manage.py db init (once per env)
	python manage.py db migrate
	python manage.py db upgrade

Remote:
	heroku run python manage.py db upgrade --app clearwater-2015
'''
