from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FloatField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange

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

# Adding/Editing products for Admin Dashboard
class ProductForm(FlaskForm):
    name = StringField("Product Name", validators=[DataRequired(), Length(max=100)])
    description = TextAreaField("Description", validators=[DataRequired()])
    price = FloatField("Price", validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField("Stock", validators=[DataRequired(), NumberRange(min=0)])
    image = StringField("Image Filename", validators=[DataRequired()])
    submit = SubmitField("Save Product")