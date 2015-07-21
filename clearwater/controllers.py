from flask import Flask, flash, redirect, render_template, request, session, url_for
from sqlalchemy.orm import sessionmaker
from clearwater import app
from models import engine, User, Measurement

app.secret_key = 'secret_key'
Session = sessionmaker(bind=engine)
s = Session()

@app.route('/')
def index():
	if not session.get('logged_in'):
		return render_template('login.html')
	else:
		return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'GET':
		return redirect(url_for('index'))
	else:
		u = str(request.form['username'])
		p = str(request.form['password'])
		query = s.query(User).filter(User.username.in_([u]), User.password.in_([p]))
		result = query.first()
		if result:
			session['logged_in'] = True
			session['username'] = result.username
		else:
			flash('Invalid username/password.')
		return redirect(url_for('index'))

@app.route('/logout')
def logout():
	session['logged_in'] = False
	if 'user' in session:
		del session['user']
	return redirect(url_for('index'))

@app.route('/user', methods=['GET', 'POST', 'DELETE'])
def manageUsers():
	if request.method == 'GET':
		#TODO: show list of users
		pass
	elif request.method == 'POST':
		#TODO: store user in db
		pass
	else:
		#TODO: frontend - warn user first
		query = s.query(User).filter(User.username.in_([session['username']]))
		result = query.first()
		s.delete(result)
		s.commit()