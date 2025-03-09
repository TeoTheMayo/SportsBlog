from flask import Flask, render_template, url_for, request, redirect, session, jsonify
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, BooleanField, RadioField, Form, SubmitField, TextAreaField, validators
from wtforms.validators import DataRequired
import configparser
import bcrypt
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

config = configparser.ConfigParser()
config.read('config.conf')

app = Flask(__name__)
app.config["SECRET_KEY"] = config["DEFAULT"]["SECRET_KEY"]
app.config["SQLALCHEMY_DATABASE_URI"] = config["DEFAULT"]["SQLALCHEMY_DATABASE_URI"]
app.config["WTF_CSRF_ENABLED"] = True
db = SQLAlchemy(app)

class SignInForms(FlaskForm):
    user_email = StringField('Email', validators=[DataRequired()])
    user_password = StringField('Password', validators=[DataRequired()])
    user_submit = SubmitField('Create Account')

class SignIns(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Minimal database creation
def ensure_db():
    uri = config["DEFAULT"]["SQLALCHEMY_DATABASE_URI"]
    db_name = uri.split('/')[-1]
    conn = psycopg2.connect(dbname="postgres", user="your_db_user", password="your_db_password", host="localhost")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
    if not cur.fetchone():
        cur.execute(f"CREATE DATABASE {db_name}")
        print(f"Database '{db_name}' created.")
    cur.close()
    conn.close()

@app.route('/', methods=["GET", "POST"])
def index():
    return render_template("dashboard.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    form = SignInForms()
    return render_template("login.html", form=form)

@app.route('/singup', methods=["GET", "POST"])
def signup():
    return render_template("singup.html")

@app.route('/submit', methods=["GET", "POST"])
def signup_submit():
    form = SignInForms()
    if request.method == "POST" and form.validate_on_submit():
        print("Form validated")
        email = form.user_email.data
        password = form.user_password.data.encode('utf-8')

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password, salt)

        user_settings = SignIns(
            email=email,
            password=hashed_password.decode('utf-8')
        )
        try:
            db.session.add(user_settings)
            db.session.commit()
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
            return render_template('signup.html', form=form, error="An error occurred during registration")

    return render_template("dashboard.html", form=form)

if __name__ == '__main__':
    app.run(debug=True)