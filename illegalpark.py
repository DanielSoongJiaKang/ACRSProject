from flask import Blueprint, render_template, flash, request, current_app, redirect, url_for
from flask_login import  login_required, current_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import TrackVehicle, VehicleAudit
from datetime import datetime, date
from functools import wraps
import pytz


import os
import requests

from . import db
from werkzeug.utils import secure_filename

from PIL import Image,ImageOps

illegalpark = Blueprint('illegalpark', __name__)

engine = create_engine("mysql+mysqlconnector://ACRSProject:Password...12345@ACRSProject.mysql.pythonanywhere-services.com/ACRSProject$ACRSDB")
Session = sessionmaker(bind=engine)
session = Session()

def admin_required(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if current_user.roles != "Admin":
                flash("You don't have permission to access this resource.", category="warning")
                return redirect(url_for("views.home"))
            return func(*args, **kwargs)
        return decorated_view

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

    #check file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def imageprocess(filename):
    regions = ['sg'] # Change to your country
    with open(filename, 'rb') as fp:
        response = requests.post(
            'https://api.platerecognizer.com/v1/plate-reader/',
             data=dict(regions=regions),  # Optional
            files=dict(upload=fp),
            headers={'Authorization': 'Token 37649c697240c794ff946cce1c0132d8af2aaf54'})
    result = response.json()
    try:
        plate = result['results'][0]['plate']
        return(plate)
    except:
        return ('Could not find plate number please retake again')

@illegalpark.route('/vehicleinfo')
@login_required
def vehicleinfo():

    track = TrackVehicle.query

    return render_template("vehicleinfo.html", user=current_user, track=track)

@illegalpark.route('/checkvehicles', methods=['GET','POST'])
@login_required
def checkvehicles():
    #check file request
    if request.method == 'POST':
        if 'photos' not in request.files:
            flash("No files are selected", category="warning")
            return render_template('checkvehicles.html', user=current_user)
        photo = request.files['photos']


        if photo.filename == '':
            flash("No Selected File", category="warning")
            return render_template("checkvehicles.html" , user=current_user)

        if photo and allowed_file(photo.filename):
            #save image and compress it
            new_filename = secure_filename(photo.filename)
            photo.save(os.path.join(current_app.config["UPLOAD_FOLDER"], new_filename))






            #compress image to <3mb
            pic = Image.open(os.path.join(current_app.config["UPLOAD_FOLDER"], new_filename))
            pic = ImageOps.exif_transpose(pic)
            pic.save(os.path.join(current_app.config["UPLOAD_FOLDER"], new_filename),optimize=True,quality=30)


             #extract text from image
            extracted_text = imageprocess(os.path.join(current_app.config["UPLOAD_FOLDER"], new_filename)).upper()



            #check if valid
            if extracted_text == 'Could not find plate number please retake again'.upper():
                flash("Could not find plate number please retake again", category="error")
                return render_template('checkvehicles.html' , user=current_user)

            else:
                GMT = pytz.timezone('Singapore')

                datetime_gmt = datetime.now(GMT)
                datetimeformat = datetime_gmt.strftime("%Y-%m-%d %H:%M:%S")

                vehicleno = TrackVehicle.query.filter_by(vehicleno=extracted_text).filter(TrackVehicle.startdatetime.contains(date.today())).first()

                if vehicleno:
                    vehicleno.enddatetime = datetimeformat
                    db.session.commit()

                    datediff = vehicleno.enddatetime - vehicleno.startdatetime
                    datediff = datediff*60

                    user=current_user.name
                    vehicleno.name= user

                    vehicleno.duration = datediff
                    db.session.commit()

                    if vehicleno.duration >= 30:
                        checkwarning = VehicleAudit.query.filter_by(vehicleno=vehicleno.vehicleno).first()
                        if checkwarning:
                            db.session.delete(vehicleno)
                            checkwarning.numofcaught +=1
                            db.session.commit()
                        else:
                            warning = VehicleAudit(vehicleno=vehicleno.vehicleno,datetimescanned=datetimeformat,name=current_user.name, status="Warning", numofcaught=1)
                            db.session.add(warning)
                            db.session.delete(vehicleno)
                            db.session.commit()


                else:


                    trackcar = TrackVehicle(vehicleno=extracted_text, startdatetime=datetimeformat, duration=0, name=current_user.name)
                    db.session.add(trackcar)
                    db.session.commit()
                return redirect('https://acrsproject.pythonanywhere.com/vehicleinfo', code=302)

    return render_template("checkvehicles.html", user=current_user)


@illegalpark.route('/vehicleinfodelete/<id>/', methods = ['GET', 'POST'])
@login_required
@admin_required
def vehicleinfodelete(id):

    data = TrackVehicle.query.get(id)
    db.session.delete(data)
    db.session.commit()
    flash("Vehicle Deleted Successfully!")

    return redirect(url_for('illegalpark.vehicleinfo'))

@illegalpark.route('/insertvehicle', methods = ['GET', 'POST'])
@login_required
def insertvehicle():
    if request.method == 'POST':
        insert = request.form.get('insert').strip()
        insert.upper()
        GMT = pytz.timezone('Singapore')

        datetime_gmt = datetime.now(GMT)
        datetimeformat = datetime_gmt.strftime("%Y-%m-%d %H:%M:%S")

        vehicleno = TrackVehicle.query.filter_by(vehicleno=insert).filter(TrackVehicle.startdatetime.contains(date.today())).first()

        if vehicleno:
            vehicleno.enddatetime = datetimeformat
            db.session.commit()

            datediff = vehicleno.enddatetime - vehicleno.startdatetime
            datediff = datediff*60
            user=current_user.name
            vehicleno.name= user

            vehicleno.duration = datediff
            db.session.commit()

            if vehicleno.duration >= 30:
                checkwarning = VehicleAudit.query.filter_by(vehicleno=vehicleno.vehicleno).first()
                if checkwarning:
                    db.session.delete(vehicleno)
                    checkwarning.numofcaught +=1
                    db.session.commit()
                else:
                    warning = VehicleAudit(vehicleno=vehicleno.vehicleno,datetimescanned=datetimeformat,name=current_user.name, status="Warning", numofcaught=1)
                    db.session.add(warning)
                    db.session.delete(vehicleno)
                    db.session.commit()

        else:
            trackcar = TrackVehicle(vehicleno=insert, startdatetime=datetimeformat, duration=0, name = current_user.name)
            db.session.add(trackcar)
            db.session.commit()
        return redirect('https://acrsproject.pythonanywhere.com/vehicleinfo', code=302)

    return render_template("checkvehicles.html", user=current_user)

@illegalpark.route('/warning')
@login_required
def warning():
    track = VehicleAudit.query.filter_by(status="Warning")

    for rows in track:
        if rows.numofcaught >=5:
            rows.status = "Blacklist"
        elif rows.numofcaught <5:
            rows.status = "Warning"
    db.session.commit()

    return render_template("warning.html", user=current_user, track =track )

@illegalpark.route('/blacklist')
@login_required
def blacklist():
    track = VehicleAudit.query.filter_by(status="Blacklist")
    for rows in track:
        if rows.numofcaught >=5:
            rows.status = "Blacklist"
        elif rows.numofcaught <5:
            rows.status = "Warning"
    db.session.commit()

    return render_template("blacklist.html", user=current_user, track=track)

@illegalpark.route('/vehicleauditdelete/<id>/', methods = ['GET', 'POST'])
@login_required
@admin_required
def vehicleauditdelete(id):

    data = VehicleAudit.query.get(id)
    db.session.delete(data)
    db.session.commit()
    flash("Vehicle Deleted Successfully!")

    return redirect(url_for('illegalpark.warning'))

