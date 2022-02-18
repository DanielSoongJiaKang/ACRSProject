from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Events, EntryVehicle, User, UserAudit
from . import db
from flask_login import login_required,  current_user
from datetime import datetime
from functools import wraps
import pytz




views = Blueprint('views', __name__)


def admin_required(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if current_user.roles != "Admin":
                flash("You don't have permission to access this resource.", category="warning")
                return redirect(url_for("views.home"))
            return func(*args, **kwargs)
        return decorated_view

@views.route('/')
def home():
    all_events = Events.query.all()

    return render_template("home.html", user=current_user, events=all_events)


@views.route('/addevents' , methods=['GET','POST'])
@login_required
@admin_required
def createEvents():
    if request.method == 'POST':
        title = request.form['eventname']
        start = request.form['startdate']
        end = request.form['enddate']
        eventtype = request.form['eventtype']
        description = request.form['description']

        start = datetime.strptime(start, "%Y-%m-%dT%H:%M")
        end = datetime.strptime(end, "%Y-%m-%dT%H:%M")
        datediff = (end-start)
        convsec = datediff.total_seconds()
        diff = convsec/60


        event = Events.query.filter_by(eventname=title, startdate=start, enddate=end).first()
        if event:
            flash('Event on the same day already exist please choose a different day', category="error")
        if len(title) < 3:
            flash('Your event title is too short!')
        elif diff <0:
            flash('Your end date should not be before start date!', category="error")
        elif len(description) < 3:
            flash('Please enter a description for events', category="error")
        else:
            if eventtype == 'Lockdown':
                new_event = Events(eventname=title,startdate=start,enddate=end,colorcode='#FF0000',eventtype=eventtype,
                                eventdes=description)
                GMT = pytz.timezone('Singapore')
                now = datetime.now(GMT)
                datetimeformat = datetime.strftime(now,"%Y-%m-%d %H:%M:%S")
                new_audit = UserAudit(datetime=datetimeformat, email=current_user.id, action="Created a lockdown event: " + title )
                db.session.add(new_audit)
                db.session.add(new_event)
                db.session.commit()
                flash('New Lockdown Created!' , category='success')
                return redirect(url_for('views.home'))
            else:
                new_event = Events(eventname=title,startdate=start,enddate=end,colorcode='#0000FF',eventtype=eventtype,
                                eventdes=description)
                GMT = pytz.timezone('Singapore')
                now = datetime.now(GMT)
                datetimeformat = datetime.strftime(now,"%Y-%m-%d %H:%M:%S")
                new_audit = UserAudit(datetime=datetimeformat, email=current_user.id, action="Created an event: " + title )
                db.session.add(new_audit)
                db.session.add(new_event)
                db.session.commit()
                flash('New Events Created!' , category='success')
                return redirect(url_for('views.home'))


    return render_template("addevent.html" , user=current_user)

@views.route('/eventlist')
@login_required
@admin_required
def eventlist():
    datetimestart = ""
    datetimeend = ""
    eventstartdates = []
    eventenddates = []
    events = Events.query.order_by(Events.id.desc()).all()
    for i in events:
        datetimestart = datetime.strftime(i.startdate,"%Y-%m-%dT%H:%M")
        eventstartdates.append(datetimestart)
        datetimeend = datetime.strftime(i.enddate,"%Y-%m-%dT%H:%M")
        eventenddates.append(datetimeend)



    return render_template('eventlist.html', user = current_user, events = events)

@views.route('/eventupdate', methods = ['GET', 'POST'])
@login_required
@admin_required
def updateevents():

    if request.method == 'POST':
        my_data = Events.query.get(request.form.get('id'))

        my_data.eventname = request.form['updatetitle']
        my_data.startdate = request.form['eventstartdate']
        my_data.enddate = request.form['eventenddate']
        my_data.eventtype = request.form['updateeventtype']
        my_data.eventdes = request.form['updateeventdes']


        if (my_data.eventtype == “Lockdown”):
            my_data.colorcode = ‘#FF0000’
        else
            my_data.colorcode = ‘#0000FF’

        GMT = pytz.timezone('Singapore')
        now = datetime.now(GMT)
        datetimeformat = datetime.strftime(now,"%Y-%m-%d %H:%M:%S")
        new_audit = UserAudit(datetime=datetimeformat, email=current_user.id, action="Update in Event Management Event ID: " + str(my_data.id))
        db.session.add(new_audit)
        db.session.commit()
        flash("Event Updated Successfully")

        return redirect(url_for('views.eventlist'))


@views.route('/eventdelete', methods = ['GET', 'POST'])
@login_required
@admin_required
def deleteevents():
    i = 0
    if request.method == 'POST':
        for getid in request.form.getlist('mycheckbox'):
            db.session.execute("DELETE FROM events WHERE id = {0}".format(getid))
            db.session.commit()
            i+=1
    GMT = pytz.timezone('Singapore')
    now = datetime.now(GMT)
    datetimeformat = datetime.strftime(now,"%Y-%m-%d %H:%M:%S")
    new_audit = UserAudit(datetime=datetimeformat, email=current_user.id, action="Multiple Delete in Event Management rows affected " + str(i))
    db.session.add(new_audit)
    db.session.commit()

    flash('Successfully Deleted!')

    return redirect(url_for('views.eventlist'))

@views.route('/eventdetails,<id>')
def eventdetail(id):

    event = Events.query.filter_by(id = id).first()
    startdatetimeformat = event.startdate.strftime("%Y-%m-%d")
    enddatetimeformat = event.enddate.strftime("%Y-%m-%d")

    entryvehicle = EntryVehicle.query.filter(EntryVehicle.datetime.between(startdatetimeformat, enddatetimeformat)).join(User, EntryVehicle.email == User.id)


    return render_template("eventdetails.html", user = current_user, event=event, entryvehicle=entryvehicle)
