from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from . import db
from flask_login import  login_required,  current_user, logout_user
from .forms import UpdateAccountForm, RequestResetForm, ResetPasswordForm, ChangePasswordForm, CheckPasswordForm
from werkzeug.security import generate_password_hash, check_password_hash
from .utils import send_reset_email




account = Blueprint('account', __name__)

@account.route("/account", methods=['GET', 'POST'])
@login_required
def acc():
    form = UpdateAccountForm()
    if form.validate_on_submit():


        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.contact = form.contact.data

        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect('https://acrsproject.pythonanywhere.com/account', code=302)
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.contact.data = current_user.contact

    return render_template('account.html', title='Account', form=form, user=current_user)

@account.route("/checkpassword", methods=['GET', 'POST'])
def checkpassword():
    form = CheckPasswordForm()
    checkpw = check_password_hash(current_user.password, current_user.password)
    if form.validate_on_submit():
        email = current_user.email
        password = form.password.data
        checkpw = User.query.filter_by(email=email).first()
        if check_password_hash(checkpw.password, password):
            return redirect('https://acrsproject.pythonanywhere.com/changepassword', code=302)
        else:
            flash('Value entered does not match current password.', 'error')
    return render_template('checkcurrentpassword.html', title='Check Password', form=form, checkpw=checkpw, user=current_user)

@account.route("/changepassword", methods=['GET', 'POST'])
def changepassword():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.password = form.newpassword.data

        if current_user.password != "":
            current_user.password = generate_password_hash(current_user.password, method ='sha256')

        db.session.commit()
        flash('Your password has been updated!', 'success')
        return redirect('https://acrsproject.pythonanywhere.com/account', code=302)
    return render_template('changepassword.html', title='Change Password', form=form, user=current_user)


@account.route("/reset_password", methods=['GET', 'POST'])
def reset_request():

    form = RequestResetForm()
    if form.validate_on_submit():
        logout_user()
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect('https://acrsproject.pythonanywhere.com/login', code=302)
    return render_template('reset_request.html', title='Reset Password', form=form, user=current_user)


@account.route("/reset_password,<token>", methods=['GET', 'POST'])
def reset_token(token):
#    if current_user.is_authenticated:
#        return redirect(url_for('account.acc'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('account.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = generate_password_hash(form.password.data, method ='sha256')
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('auth.login'))
    return render_template('reset_token.html', title='Reset Password', form=form, user=current_user)