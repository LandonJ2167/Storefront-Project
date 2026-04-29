from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[
        DataRequired(),
        Email(),
        Length(max=120)
    ])
    password = PasswordField("Password", validators=[
        DataRequired(),
        Length(min=6, message="Password must be at least 6 characters long.")
    ])
    confirm_password = PasswordField("Confirm Password", validators=[
        DataRequired(),
        EqualTo("password", message="Passwords must match.")
    ])
    role = SelectField("Account Type", choices=[
        ("customer", "Customer"),
        ("manager", "Manager")
    ])
    submit = SubmitField("Create Account")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[
        DataRequired(),
        Email()
    ])
    password = PasswordField("Password", validators=[
        DataRequired()
    ])
    submit = SubmitField("Login")