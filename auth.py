from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, UserAudit
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from functools import wraps
from .utils import notify
import pytz
from datetime import datetime


auth = Blueprint('auth', __name__)

def admin_required(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if current_user.roles != "Admin":
                flash("You don't have permission to access this resource.", category="warning")
                return redirect(url_for("views.home"))
            return func(*args, **kwargs)
        return decorated_view

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    else:
        if request.method == 'POST':
            email = request.form.get('emaillogin')
            password = request.form.get('passwordlogin')

            user = User.query.filter_by(email=email).first()
            if user:
                if check_password_hash(user.password, password):
                    flash('Logged in successfully!' , category='success')
                    login_user(user, remember=True)
                    return redirect(url_for('views.home'))


                else:
                    flash('Incorrect password try again!', category='error')
            else:
                flash('Email does not exist.', category='error')

    return render_template('login.html', user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/admincreateuser', methods=['GET','POST'])
@login_required
@admin_required
def create():
    if request.method == 'POST':
        email = request.form.get('emailreg')
        password = request.form.get('passwordreg')
        roles = request.form.get('rolesreg')
        name = request.form.get('namereg')
        contact = request.form.get('contactreg')
        status = request.form.get('status')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exist', category='error')
        elif len(email) <4 :
            flash('Email must contain more than 4 characters', category='error')
        elif len(password) <6:
            flash('Password must contain more than 6 characters', category='error')
        elif len(name) <3:
            flash('Name must contain more than 3 characters', category='error')
        elif len(contact) <8:
            flash('Contact Number must contain more than 8 characters', category='error')
        elif len(status) <1:
            flash('Please specify user status', category='error')
        else:
            new_user = User(email=email,password=generate_password_hash(password, method ='sha256'),
               roles=roles, name=name,contact=contact, status=status)
            GMT = pytz.timezone('Singapore')
            now = datetime.now(GMT)
            datetimeformat = datetime.strftime(now,"%Y-%m-%d %H:%M:%S")
            new_audit = UserAudit(datetime=datetimeformat, email=current_user.id, action="Create new User:" + email +  " in User Management")
            db.session.add(new_audit)
            db.session.add(new_user)
            notify(new_user)
            db.session.commit()
            flash('Account Created!' , category='success')
            return redirect(url_for('userlist.list'))

    return render_template('admincreateuser.html', user=current_user)