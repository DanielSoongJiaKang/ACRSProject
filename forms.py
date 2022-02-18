from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email, ValidationError, EqualTo
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask import redirect, url_for

class UpdateAccountForm(FlaskForm):
    name = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    contact = StringField('Contact', validators=[DataRequired(), Length(max=8)])

    submit = SubmitField('Update')

    def validate_name(self, name):
        if name.data != current_user.name:
            user = User.query.filter_by(name=name.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

    def validate_contact(self, contact):
        if contact.data != current_user.contact:
            user = User.query.filter_by(contact=contact.data).first()
            if user:
                raise ValidationError('That number is taken. Please choose a different one.')

class ChangePasswordForm(FlaskForm):
    newpassword = PasswordField('New Password', validators=[DataRequired(), Length(max=20)])
    confirmpassword = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('newpassword')])

    submit = SubmitField('Change Password')

class CheckPasswordForm(FlaskForm):
    password = PasswordField('Current Password', validators=[DataRequired()])

    submit = SubmitField('Check Password')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])

    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
