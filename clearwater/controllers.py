from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from flask.ext.login import LoginManager, current_user, login_required, login_user, logout_user
from clearwater import app
from models import User, Measurement, login_serializer
import md5

app.secret_key = 'secret_key'
lm = LoginManager()
lm.init_app(app)

# -----------------------------------------------
# LOGIN MANAGER CONFIG
# -----------------------------------------------
lm.login_view = 'index'
# lm.refresh_view = 'reauthenticate'

@lm.user_loader
def load_user(userid):
	return User.get(userid)

@lm.token_loader
def load_token(token):
	max_age = app.config['REMEMBER_COOKIE_DURATION'].total_seconds()
	data = login_serializer.loads(token, max_age=max_age)
	user = User.get(data[0])
	if user and data[1] == user.password:
		return user
	return None

# -----------------------------------------------
# UTIL
# -----------------------------------------------
def hash_pass(password):
	saltedPass = password + app.secret_key
	return md5.new(saltedPass).hexdigest()

# -----------------------------------------------
# ROUTES
# -----------------------------------------------
@app.route('/')
def index():
	if current_user.is_anonymous():
		return render_template('login.html', nxt=request.args.get('next'))
	else:
		return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'GET':
		return redirect(url_for('index'))
	elif request.method == 'POST':
		u = str(request.form['username'])
		p = str(request.form['password'])
		user = User.get(u)
		if user:
			if user.password == hash_pass(p):
				session['username'] = user.username
				login_user(user, remember=('rememberme' in request.form))
				# TODO: validate the 'next' parameter (protect from "open redirect" vulnerability)
			else:
				flash('Invalid password.')
		else:
			flash('Invalid username.')
		
		if request.form['next'] != 'None':
			return redirect(str(request.form['next']))
		else:
			return redirect(url_for('index'))

@app.route('/logout')
def logout():
	logout_user()
	if 'username' in session:
		del session['username']
	return redirect(url_for('index'))

@app.route('/users', methods=['GET', 'POST', 'DELETE'])
@login_required
def manageUsers():
	if request.method == 'GET':
		users = User.getAll()
		return render_template('users.html', users=users)
	elif request.method == 'POST':
		u = str(request.form['username'])
		p = str(request.form['password'])
		user = User(u, hash_pass(p))
		User.create(user)
	elif request.method == 'DELETE':
		#TODO: frontend - warn user first
		user = User.get(session['username'])
		User.delete(user)

@app.route('/measurements', methods=['GET', 'POST', 'DELETE'])
@login_required
def manageMeasurements():
	if request.method == 'GET':
		return render_template('measurements.html')
	elif request.method == 'POST':
		pass
	elif request.method == 'DELETE':
		pass
