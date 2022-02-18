from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Appeal, VehicleAudit
from flask_mail import Mail, Message
from . import db
from .utils import approve, reject
from flask_login import login_required, current_user
from functools import wraps


appeal = Blueprint('appeal', __name__)

def admin_required(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if current_user.roles != "Admin":
                flash("You don't have permission to access this resource.", "warning")
                return redirect(url_for("views.home"))
            return func(*args, **kwargs)
        return decorated_view


@appeal.route('/appeal', methods = ['GET','POST'])
def insert():

    if request.method == 'POST':
        vehicleno = request.form['vehicleno']
        name = request.form['name']
        email = request.form['email']
        reason = request.form['reason']

        vehaudit = VehicleAudit.query.filter_by(vehicleno=vehicleno).first()

        if vehaudit:
            if len(vehicleno) <= 7 and len(vehicleno) > 8:
                flash('Vehicle number invalid' , category='error')
            elif len(name) <2:
                flash('Name must be more than 1 character' , category='error')
            elif len(reason) < 10 and len(reason) > 2000:
                flash('Reason must be between 10 - 2000 characters', category='error')
            else:
                my_data = Appeal(vehicleno=vehicleno, name=name, reason=reason, email=email)
                db.session.add(my_data)
                db.session.commit()
                flash("Appeal submitted! It will take 2-3 days for the officer to get back to you through email!")
                return render_template("appeal.html", user=current_user)
        else:
            flash("Vehicle Number does not exist in blacklist!", category='error')


    return render_template("appeal.html", user=current_user)



@appeal.route('/appeallist')
@login_required
@admin_required
def Index():
    all_data = Appeal.query
    return render_template("appeallist.html", appeal = all_data, user=current_user)



@appeal.route('/appealapprove,<id>,<email>', methods = ['GET', 'POST'])
@login_required
@admin_required
def appealapprove(id,email):

    user = Appeal.query.filter_by(email = email).first()

    my_data = Appeal.query.get(id)
    approve(user,my_data.vehicleno)

    delete = VehicleAudit.query.filter_by(vehicleno=my_data.vehicleno).first()
    db.session.delete(delete)

    db.session.delete(my_data)
    db.session.commit()
    flash("Appeal Approved!")

    return redirect(url_for('appeal.Index'))


@appeal.route('/appealreject,<id>,<email>', methods = ['GET', 'POST'])
@login_required
@admin_required
def appealreject(id,email):

    user = Appeal.query.filter_by(email = email).first()

    my_data = Appeal.query.get(id)
    reject(user,my_data.vehicleno)

    db.session.delete(my_data)
    db.session.commit()
    flash("Appeal Rejected!")

    return redirect(url_for('appeal.Index'))


@appeal.route('/about', methods = ['GET','POST'])
def about():
    return render_template("about.html", user=current_user)

