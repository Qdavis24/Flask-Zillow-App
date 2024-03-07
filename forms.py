from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired, Length, Email


class Register(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(min=5, max=20), Email()])
    name = StringField("Name", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=7, max=20)])
    submit = SubmitField(render_kw={"class": "mt-5"})


class Login(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField(render_kw={"class": "mt-5"})