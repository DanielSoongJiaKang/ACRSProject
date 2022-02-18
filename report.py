from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import create_engine, extract
from sqlalchemy.orm import sessionmaker, aliased
from .models import EntryVehicle, VehicleAudit, Vehicle, Events, User, Post
from sqlalchemy.types import Integer
from sqlalchemy.sql import func
from functools import wraps
from . import db
from sqlalchemy import or_, union

reports = Blueprint('reports', __name__)

def admin_required(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if current_user.roles != "Admin":
                flash("You don't have permission to access this resource.", category="warning")
                return redirect(url_for("views.home"))
            return func(*args, **kwargs)
        return decorated_view


engine = create_engine("mysql+mysqlconnector://ACRSProject:Password...12345@ACRSProject.mysql.pythonanywhere-services.com/ACRSProject$ACRSDB")
Session = sessionmaker(bind=engine)
session = Session()


@reports.route('/report')
@login_required
@admin_required
def report():

    app_count = func.count(EntryVehicle.access)

    query1 = session.query(app_count.label("approved"), EntryVehicle.datetime.label("year")).filter(EntryVehicle.access=="Approved").group_by(func.year(EntryVehicle.datetime))

    query2 = session.query(app_count.label("denied"), EntryVehicle.datetime.label("year")).filter(EntryVehicle.access=="Denied").group_by(func.year(EntryVehicle.datetime))

    entry_count = func.count(EntryVehicle.access.cast(Integer))

    output = session.query(entry_count.label("total"),EntryVehicle.datetime.label("year")).filter(EntryVehicle.access=="Approved").group_by(func.year(EntryVehicle.datetime)).all()

    company_count = func.count(Vehicle.id)

    result = session.query(company_count.label("total"), Vehicle.company.label("company")).group_by(Vehicle.company).all()

    enter_count = func.count(VehicleAudit.status.cast(Integer))

    out = session.query(enter_count.label("total"), VehicleAudit.datetimescanned.label("year")).filter(VehicleAudit.status=="Warning").group_by(func.year(VehicleAudit.datetimescanned)).all()

    audit_count = func.count(VehicleAudit.status.cast(Integer))

    outcome = session.query(audit_count.label("total"), VehicleAudit.datetimescanned.label("year")).filter(VehicleAudit.status=="Blacklist").group_by(func.year(VehicleAudit.datetimescanned)).all()

    event_count = func.count(Events.eventtype)

    query3 = session.query(event_count.label("event"), Events.startdate.label("year")).filter(Events.eventtype=="Event").group_by(func.year(Events.startdate))

    query4 = session.query(event_count.label("lockdown"), Events.startdate.label("year")).filter(Events.eventtype=="Lockdown").group_by(func.year(Events.startdate))

    holder_count = func.count(Vehicle.id)

    results = session.query(holder_count.label("total"), Vehicle.holdertype.label("holdertype")).group_by(Vehicle.holdertype).all()

    offence_count = func.count(VehicleAudit.id)

    sum = session.query(offence_count.label("total"), VehicleAudit.numofcaught.label("offence")).filter(VehicleAudit.status=="Warning").group_by(VehicleAudit.numofcaught)

    user_count = func.count(User.id)

    sums = session.query(user_count.label("total"), User.status.label("status")).group_by(User.status).all()

    cat_count = func.count(Post.id)

    categ = session.query(cat_count.label("total"), Post.category.label("category")).group_by(Post.category).all()

    stat_count = func.count(Post.id)

    stats = session.query(stat_count.label("total"), Post.status.label("status")).filter(Post.category=="Bug").group_by(Post.status)

    return render_template("report.html", output=output, query1=query1, query2=query2, result=result, out=out, outcome=outcome, query3=query3, query4=query4, results=results, sum=sum, sums=sums, categ=categ, stats=stats, user=current_user)

@reports.route('/reportentry')
@login_required
@admin_required
def reportentry():

    app_count = func.count(EntryVehicle.access)

    query1 = session.query(app_count.label("approved"), EntryVehicle.datetime.label("year")).filter(EntryVehicle.access=="Approved").group_by(func.year(EntryVehicle.datetime))

    query2 = session.query(app_count.label("denied"), EntryVehicle.datetime.label("year")).filter(EntryVehicle.access=="Denied").group_by(func.year(EntryVehicle.datetime))


    return render_template("reportentry.html", query1=query1, query2=query2, user=current_user)

@reports.route('/reportentrymonth<id>')
@login_required
@admin_required
def reportentrymonth(id):

    app_count = func.count(EntryVehicle.access)

    query1 = session.query(app_count.label("approved"), EntryVehicle.datetime.label("month")).filter(EntryVehicle.access=="Approved", extract('year', EntryVehicle.datetime) == id).group_by(func.month(EntryVehicle.datetime)).all()

    query2 = session.query(app_count.label("denied"), EntryVehicle.datetime.label("month")).filter(EntryVehicle.access=="Denied", extract('year', EntryVehicle.datetime) == id).group_by(func.month(EntryVehicle.datetime)).all()

    return render_template("reportentrymonth.html", query1=query1, query2=query2, user=current_user)

@reports.route('/reportapproved')
@login_required
@admin_required
def reportapproved():


    entry_count = func.count(EntryVehicle.access)


    output = session.query(entry_count.label("total"),EntryVehicle.datetime.label("year")).filter(EntryVehicle.access=="Approved").group_by(func.year(EntryVehicle.datetime)).all()

    return render_template("reportapproved.html" , output=output, user=current_user)

@reports.route('/reportapprovedmonth<id>')
@login_required
@admin_required
def reportapprovedmonth(id):

    entry_count = func.count(EntryVehicle.access)

    output = session.query(entry_count.label("total"),EntryVehicle.datetime.label("month")).filter(EntryVehicle.access=="Approved", extract('year', EntryVehicle.datetime) == id).group_by(func.month(EntryVehicle.datetime)).all()

    return render_template("reportapprovedmonth.html", output=output, user=current_user )

@reports.route('/reportapprovedday<id>,<year>')
@login_required
@admin_required
def reportapprovedday(id, year):

    entry_count = func.count(EntryVehicle.access)

    output = session.query(entry_count.label("total"), EntryVehicle.datetime.label("day")).filter(EntryVehicle.access=="Approved", extract('month', EntryVehicle.datetime) == id, extract('year', EntryVehicle.datetime) == year).group_by(func.day(EntryVehicle.datetime)).all()

    return render_template("reportapprovedday.html", output=output, user=current_user )

@reports.route('/reportwarning')
@login_required
@admin_required
def reportwarning():

    enter_count = func.count(VehicleAudit.status.cast(Integer))

    out = session.query(enter_count.label("total"), VehicleAudit.datetimescanned.label("year")).filter(VehicleAudit.status=="Warning").group_by(func.year(VehicleAudit.datetimescanned)).all()

    return render_template("reportwarning.html" , out=out, user=current_user)

@reports.route('/reportwarningmonth<id>')
@login_required
@admin_required
def reportwarningmonth(id):

    enter_count = func.count(VehicleAudit.status.cast(Integer))

    out = session.query(enter_count.label("total"), VehicleAudit.datetimescanned.label("month")).filter(VehicleAudit.status=="Warning", extract('year', VehicleAudit.datetimescanned) == id).group_by(func.month(VehicleAudit.datetimescanned)).all()

    return render_template("reportwarningmonth.html", out=out, user=current_user )

@reports.route('/reportwarningday<id>,<year>')
@login_required
@admin_required
def reportwarningday(id, year):

    enter_count = func.count(VehicleAudit.status.cast(Integer))


    out = session.query(enter_count.label("total"),VehicleAudit.datetimescanned.label("day")).filter(VehicleAudit.status=="Warning", extract('month', VehicleAudit.datetimescanned) == id, extract('year', VehicleAudit.datetimescanned) == year).group_by(func.day(VehicleAudit.datetimescanned)).all()

    return render_template("reportwarningday.html", out=out, user=current_user )

@reports.route('/reportblacklist')
@login_required
@admin_required
def reportblacklist():

    audit_count = func.count(VehicleAudit.status.cast(Integer))


    outcome = session.query(audit_count.label("total"),VehicleAudit.datetimescanned.label("year")).filter(VehicleAudit.status=="Blacklist").group_by(func.year(VehicleAudit.datetimescanned)).all()

    return render_template("reportblacklist.html" , outcome=outcome, user=current_user)

@reports.route('/reportblacklistmonth<id>')
@login_required
@admin_required
def reportblacklistmonth(id):

    audit_count = func.count(VehicleAudit.status.cast(Integer))


    outcome = session.query(audit_count.label("total"),VehicleAudit.datetimescanned.label("month")).filter(VehicleAudit.status=="Blacklist", extract('year', VehicleAudit.datetimescanned) == id).group_by(func.month(VehicleAudit.datetimescanned)).all()

    return render_template("reportblacklistmonth.html", outcome=outcome, user=current_user )

@reports.route('/reportblacklistday<id>,<year>')
@login_required
@admin_required
def reportblacklistday(id, year):

    audit_count = func.count(VehicleAudit.status.cast(Integer))

    outcome = session.query(audit_count.label("total"),VehicleAudit.datetimescanned.label("day")).filter(VehicleAudit.status=="Blacklist", extract('month', VehicleAudit.datetimescanned) == id, extract('year', VehicleAudit.datetimescanned) == year).group_by(func.day(VehicleAudit.datetimescanned)).all()

    return render_template("reportblacklistday.html", outcome=outcome, user=current_user )

@reports.route('/reportcompany')
@login_required
@admin_required
def reportcompany():

    company_count = func.count(Vehicle.id)

    result = session.query(company_count.label("total"), Vehicle.company.label("company")).group_by(Vehicle.company).all()

    return render_template("reportcompany.html", result=result, user=current_user )

@reports.route('/reportevent')
@login_required
@admin_required
def reportevent():

    event_count = func.count(Events.eventtype)

    query3 = session.query(event_count.label("event"), Events.startdate.label("year")).filter(Events.eventtype=="Event").group_by(func.year(Events.startdate))

    query4 = session.query(event_count.label("lockdown"), Events.startdate.label("year")).filter(Events.eventtype=="Lockdown").group_by(func.year(Events.startdate))

    return render_template("reportevent.html", query3=query3, query4=query4, user=current_user)


@reports.route('/reporteventmonth<id>')
@login_required
@admin_required
def reporteventmonth(id):

    event_count = func.count(Events.eventtype)

    query3 = session.query(event_count.label("event"), Events.startdate.label("month")).filter(Events.eventtype=="Event", extract('year', Events.startdate) == id).group_by(func.month(Events.startdate)).all()

    query4 = session.query(event_count.label("lockdown"), Events.startdate.label("month")).filter(Events.eventtype=="Lockdown", extract('year', Events.startdate) == id).group_by(func.month(Events.startdate)).all()

    return render_template("reporteventmonth.html", query3=query3, query4=query4, user=current_user)


@reports.route('/reportholder')
@login_required
@admin_required
def reportholder():

    holder_count = func.count(Vehicle.id)

    results = session.query(holder_count.label("total"), Vehicle.holdertype.label("holdertype")).group_by(Vehicle.holdertype).all()

    return render_template("reportholder.html", results=results, user=current_user )

@reports.route('/reportoffence')
@login_required
@admin_required
def reportoffence():

    offence_count = func.count(VehicleAudit.id)

    sum = session.query(offence_count.label("total"), VehicleAudit.numofcaught.label("offence")).filter(VehicleAudit.status=="Warning").group_by(VehicleAudit.numofcaught)

    return render_template("reportoffence.html", sum=sum, user=current_user )

@reports.route('/reportuser')
@login_required
@admin_required
def reportuser():

    user_count = func.count(User.id)

    sums = session.query(user_count.label("total"), User.status.label("status")).group_by(User.status).all()

    return render_template("reportuser.html", sums=sums, user=current_user )

@reports.route('/reportcat')
@login_required
@admin_required
def reportcat():

    cat_count = func.count(Post.id)

    categ = session.query(cat_count.label("total"), Post.category.label("category")).group_by(Post.category).all()

    return render_template("reportcat.html", categ=categ, user=current_user )

@reports.route('/reportstatus')
@login_required
@admin_required
def reportstatus():

    stat_count = func.count(Post.id)

    stats = session.query(stat_count.label("total"), Post.status.label("status")).filter(Post.category=="Bug").group_by(Post.status)

    return render_template("reportstatus.html", stats=stats, user=current_user )
