from flask import Flask, render_template, redirect, request, flash, session
from mysqlconnection import MySQLConnector
import re
import bcrypt
# import bcrypt to protect sensitive data
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
# 1 email validation 
app = Flask(__name__)
app.secret_key = "helpme"
# to add session app.secret should be after app
mysql = MySQLConnector(app, "users_db")
# to create connection with mysql connection.py
@app.route("/")
def index():
	return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
# routes to the registration page
	errors = []
# create error list or dictionary 
	if len(request.form['first']) < 1:
		errors.append("First name MUST be completed")
	elif len(request.form['first']) < 2:
		errors.append("First name MUST be longer than 1 letters.")
 # first name validation if it is empty or less than two input 
	
	if len(request.form['last']) < 1:
		errors.append("Last name MUST be completed")
	elif len(request.form['last']) < 2:
		errors.append("Last name MUST be longer than 1 letters.")
 # last name validation if it is empty or less than two input 
	if len(request.form['email']) < 1:
		errors.append("Email MUST be completed")
	elif not EMAIL_REGEX.match(request.form['email']):
		errors.append("Invalid email")
#  email validation if it is empty or contains the right format 
	if len(request.form['password']) < 1:
		errors.append("Password MUST be completed")
	elif len(request.form['password']) < 8: 
		errors.append("Password MUST be longer than 7 characters")
# password validation if it is empty or less than 8 caracter 
	if len(request.form['pass_confirm']) < 1:
		errors.append("Confirm password MUST be completed")
	elif request.form['pass_confirm'] != request.form['password']:
		errors.append("Password MUST match confirmed password")
# password confirmation if it is PW matchs  

	if errors == []:
		query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:first, :last, :email, :password, NOW(), NOW())"
#  query to insert data to SQL key word first then values in second in the arrangment found in db
        data = {
			'first' : request.form['first'],
			'last' : request.form['last'],
			'email' : request.form['email'],
			'password' : bcrypt.hashpw(request.form['password'].encode(), bcrypt.gensalt())
		}
# create dictionary the first part before colon is the same as after colon in value in query
        user_id = mysql.query_db(query, data)
# query takes the data insert as in above data before dictionary as first paramater 
        session["user_id"] = user_id
        session["user_name"] = request.form['first']

        return redirect("/success")
# redirect to success when the registration pass the validation

	for error in errors:
		flash (error)

	return redirect("/")

@app.route('/login', methods=["POST"])
def login():
	errors = []

# log in route 
	if len(request.form['email']) < 1:
		errors.append("Email MUST be completed")
	elif not EMAIL_REGEX.match(request.form['email']):
		errors.append("Invalid email")
# log in validation of password  
	if len(request.form['password']) < 1:
		errors.append("Password MUST be completed")
	elif len(request.form['password']) < 8: 
		errors.append("Password MUST be longer than 7 characters")
	
	query = "SELECT * FROM users WHERE email = '{}'".format(request.form['email'])
	resultSet = mysql.query_db(query)

	if len(resultSet) < 1:
		errors.append("The email does not exist.")
	else:
		if bcrypt.checkpw(request.form['password'].encode(),resultSet[0]['password'].encode()): 
			session["user_id"] = resultSet[0]['id']
			session["user_name"] = resultSet[0]['first_name']

			return redirect("/success")
		else:
			errors.append("Password incorrect.")


	for error in errors:
		flash (error)	

	return redirect ('/')

@app.route("/success")
def success():
	if "user_id" not in session:
		flash("you have to login first")
		return redirect("/")
	return render_template("success.html")
@app.route("/logout")
def logout():
	session.clear()
	return redirect("/")

app.run(debug=True)