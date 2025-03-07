from flask import Flask, render_template, url_for, request, redirect, session, jsonify
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, BooleanField, RadioField, Form, SubmitField, TextAreaField, validators
from wtforms.validators import DataRequired
import configparser

config = configparser.ConfigParser()
config.read('config.conf')

app = Flask(__name__)
app.config["SECRET_KEY"] = config["DEFAULT"]["SECRET_KEY"]
app.config["SQLALCHEMY_DATABASE_URI"] = config["DEFAULT"]["SQLALCHEMY_DATABASE_URI"]
app.config["WIF_CSRF_ENABLED"] = True
db = SQLAlchemy(app)

class SignInForms(FlaskForm):
    user_email = StringField('Email', validators=[DataRequired()])
    user_password = StringField('Password', validators=[DataRequired()])
    user_submit = SubmitField('Create Account')


class SignIns(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(150), unique = True, nullable = False)
    password = db.Column(db.String(150), nullable = False)


@app.route('/', methods=["GET", "POST"])
def index():
    form = SignInForms()
    return render_template("dashboard.html", form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    return render_template("login.html")

@app.route('/submit', methods=["GET", "POST"])
def submit():
    form = SignInForms()
    if form.validate_on_submit():
        print("Form validated")
        print(f"Email: {form.user_email.data}")
        print(f"Password: {form.user_password.data}")
        email = form.user_email.data
        password = form.user_password.data

        user_settings = SignIns(email=email, password=password)
        db.session.add(user_settings)
        db.session.commit()


        return redirect(url_for('index'))  # Redirect to the index page after successful login

    return render_template("dashboard.html", form=form)