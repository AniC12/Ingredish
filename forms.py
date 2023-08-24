from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired

class UserSignUpForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired()])
    first_name = StringField("First name", validators=[InputRequired()])
    last_name = StringField("Last name", validators=[InputRequired()])

class UserLoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

class SearchForm(FlaskForm):
    query = StringField("Query", validators=[InputRequired()])