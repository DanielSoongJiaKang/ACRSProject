from flask import render_template, Blueprint, flash, redirect, url_for
from flask_login import  login_required, current_user
from sqlalchemy import create_engine, extract
from sqlalchemy.orm import sessionmaker
from .models import User, VehicleAudit, EntryVehicle, Vehicle
from functools import wraps
from sqlalchemy import and_, or_

viewlist = Blueprint('viewlist', __name__)

def admin_required(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if current_user.roles != "Admin":
                flash("You don't have permission to access this resource.", category="warning")
                return redirect(url_for("report.reportuser"))
            return func(*args, **kwargs)
        return decorated_view

engine = create_engine("mysql+mysqlconnector://ACRSProject:Password...12345@ACRSProject.mysql.pythonanywhere-services.com/ACRSProject$ACRSDB")
Session = sessionmaker(bind=engine)
session = Session()

@viewlist.route('/vlist,<status>', methods = ['GET', 'POST'])
@login_required
@admin_required
def vlist(status):

    data = session.query(User.email.label("email"), User.roles.label("roles"), User.name.label("name"), User.contact.label("contact")).filter(User.status==status)


    return render_template("vlist.html", user=current_user, data=data, status=status)


@viewlist.route('/blist,<year>', methods = ['GET', 'POST'])
@login_required
@admin_required
def blist(year):

    data = session.query(VehicleAudit.vehicleno.label("vehicleno"), VehicleAudit.datetimescanned.label("month"), VehicleAudit.name.label("name")).filter(VehicleAudit.status=="Blacklist", extract('year', VehicleAudit.datetimescanned) == year)

    return render_template("blist.html", user=current_user, data=data, year=year)

@viewlist.route('/bmlist,<month>,<year>', methods = ['GET', 'POST'])
@login_required
@admin_required
def bmlist(month, year):

    data = session.query(VehicleAudit.vehicleno.label("vehicleno"), VehicleAudit.datetimescanned.label("day"), VehicleAudit.name.label("name")).filter(VehicleAudit.status=="Blacklist", extract('month', VehicleAudit.datetimescanned) == month, extract('year', VehicleAudit.datetimescanned) == year)

    return render_template("bmlist.html", user=current_user, data=data, month=month)

@viewlist.route('/bdlist,<day>,<month>', methods = ['GET', 'POST'])
@login_required
@admin_required
def bdlist(day, month):

    data = session.query(VehicleAudit.vehicleno.label("vehicleno"), VehicleAudit.name.label("name")).filter(VehicleAudit.status=="Blacklist", extract('day', VehicleAudit.datetimescanned) == day, extract('month', VehicleAudit.datetimescanned) == month)

    return render_template("bdlist.html", user=current_user, data=data, day=day)

@viewlist.route('/wlist,<year>', methods = ['GET', 'POST'])
@login_required
@admin_required
def wlist(year):

    output = session.query(VehicleAudit.vehicleno.label("vehicleno"), VehicleAudit.datetimescanned.label("month"), VehicleAudit.name.label("name")).filter(VehicleAudit.status=="Warning", extract('year', VehicleAudit.datetimescanned) == year)

    return render_template("wlist.html", user=current_user, output=output, year=year)

@viewlist.route('/wmlist,<month>,<year>', methods = ['GET', 'POST'])
@login_required
@admin_required
def wmlist(month, year):

    output = session.query(VehicleAudit.vehicleno.label("vehicleno"), VehicleAudit.datetimescanned.label("day"), VehicleAudit.name.label("name")).filter(VehicleAudit.status=="Warning", extract('month', VehicleAudit.datetimescanned) == month, extract('year', VehicleAudit.datetimescanned) == year)

    return render_template("wmlist.html", user=current_user, output=output, month=month)

@viewlist.route('/wdlist,<day>,<month>', methods = ['GET', 'POST'])
@login_required
@admin_required
def wdlist(day, month):

    output = session.query(VehicleAudit.vehicleno.label("vehicleno"), VehicleAudit.name.label("name")).filter(VehicleAudit.status=="Warning", extract('day', VehicleAudit.datetimescanned) == day, extract('month', VehicleAudit.datetimescanned) == month)

    return render_template("wdlist.html", user=current_user, output=output, day=day)

@viewlist.route('/alist,<year>', methods = ['GET', 'POST'])
@login_required
@admin_required
def alist(year):

    result = session.query(User.email.label("email"), EntryVehicle.vehicleno.label("vehicleno"), EntryVehicle.datetime.label("month")).filter(EntryVehicle.access=="Approved", extract('year', EntryVehicle.datetime) == year).join(User, EntryVehicle.email == User.id)

    return render_template("alist.html", user=current_user, result=result, year=year)

@viewlist.route('/amlist,<month>,<year>', methods = ['GET', 'POST'])
@login_required
@admin_required
def amlist(month, year):

    result = session.query(User.email.label("email"), EntryVehicle.vehicleno.label("vehicleno"), EntryVehicle.datetime.label("day")).filter(EntryVehicle.access=="Approved", extract('month', EntryVehicle.datetime) == month, extract('year', EntryVehicle.datetime) == year).join(User, EntryVehicle.email == User.id)

    return render_template("amlist.html", user=current_user, result=result, month=month)

@viewlist.route('/adlist,<day>,<month>', methods = ['GET', 'POST'])
@login_required
@admin_required
def adlist(day, month):

    result = session.query(User.email.label("email"), EntryVehicle.vehicleno.label("vehicleno")).filter(EntryVehicle.access=="Approved", extract('day', EntryVehicle.datetime) == day, extract('month', EntryVehicle.datetime) == month).join(User, EntryVehicle.email == User.id)

    return render_template("adlist.html", user=current_user, result=result, day=day)

@viewlist.route('/hlist,<holdertype>', methods = ['GET', 'POST'])
@login_required
@admin_required
def hlist(holdertype):

    put = session.query(Vehicle.holdername.label("name"), Vehicle.vehicleno.label("vehicleno"), Vehicle.model.label("model"), Vehicle.company.label("company")).filter(Vehicle.holdertype==holdertype)


    return render_template("hlist.html", user=current_user, put=put, holdertype=holdertype)

@viewlist.route('/clist,<company>', methods = ['GET', 'POST'])
@login_required
@admin_required
def clist(company):

    output = session.query(Vehicle.holdername.label("name"), Vehicle.holdertype.label("holdertype"), Vehicle.vehicleno.label("vehicleno"), Vehicle.model.label("model")).filter(Vehicle.company==company)


    return render_template("clist.html", user=current_user, output=output, company=company)

@viewlist.route('/numlist,<numofcaught>', methods = ['GET', 'POST'])
@login_required
@admin_required
def numlist(numofcaught):

    out = session.query(VehicleAudit.name.label("name"), VehicleAudit.vehicleno.label("vehicleno")).filter(VehicleAudit.numofcaught==numofcaught, VehicleAudit.status=="Warning")


    return render_template("numlist.html", user=current_user, out=out, numofcaught=numofcaught)
