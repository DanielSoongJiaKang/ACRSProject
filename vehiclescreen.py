from flask import Blueprint, render_template, flash, request, current_app
from flask_login import  login_required, current_user
import os
import requests

from . import db
from .models import Vehicle, EntryVehicle, Events, User
from datetime import datetime
from werkzeug.utils import secure_filename

from PIL import Image,ImageOps
import pytz



screen = Blueprint('screen', __name__)



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




@screen.route('/screenvehicle' , methods=['GET','POST'])
@login_required
def uploadvehicle():
    #check file request
    if request.method == 'POST':
        if 'photos' not in request.files:
            flash("No files are selected", category="error")
            return render_template('uploadvehicle.html', user=current_user)
        photo = request.files['photos']


        if photo.filename == '':
            flash("No Selected File", category="error")
            return render_template("uploadvehicle.html" , user=current_user)

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
                return render_template('uploadvehicle.html' , user=current_user)

            else:

                GMT = pytz.timezone('Singapore')
                now = datetime.now(GMT)
                datetimeformat = datetime.strftime(now,"%Y-%m-%d %H:%M:%S")
                vehicleno = Vehicle.query.filter_by(vehicleno=extracted_text).first()
                email = current_user.id
                if vehicleno:
                    entrycar = EntryVehicle(datetime=datetimeformat, vehicleno=extracted_text, email=email, access="Approved")
                    db.session.add(entrycar)
                    db.session.commit()
                    flash(extracted_text + " is APPROVED", category="success")
                else:
                    entrycar = EntryVehicle(datetime=datetimeformat, vehicleno=extracted_text, email=email, access="Denied")
                    db.session.add(entrycar)
                    db.session.commit()
                    flash(extracted_text + " IS NOT ALLOWED IN RP", category="error")


            return render_template('uploadvehicle.html' , user=current_user)
        else:
            flash("Please insert correct file", category="error")
            return render_template('uploadvehicle.html' , user=current_user)


    elif request.method == 'GET':
        return render_template('uploadvehicle.html', user=current_user)

@screen.route('/searchvehicle' , methods=['GET','POST'])
@login_required
def searchvehicle():
    if request.method == 'POST':
        #search
        search = request.form.get('search').strip()
        search.upper()
        #check
        GMT = pytz.timezone('Singapore')
        now = datetime.now(GMT)
        datetimeformat = datetime.strftime(now,"%Y-%m-%d %H:%M:%S")
        vehicleno = Vehicle.query.filter_by(vehicleno=search).first()
        email = current_user.id
        if vehicleno:
            entrycar = EntryVehicle(datetime=datetimeformat, vehicleno=search, email=email, access="Approved")
            db.session.add(entrycar)
            db.session.commit()
            flash(search + " is APPROVED", category="success")
        else:
            entrycar = EntryVehicle(datetime=datetimeformat, vehicleno=search, email=email, access="Denied")
            db.session.add(entrycar)
            db.session.commit()
            flash(search + " IS NOT ALLOWED IN RP", category="error")


        return render_template('uploadvehicle.html' , user=current_user)


@screen.route('/entryvehiclebydate')
@login_required
def entrybydate():
    all_events = Events.query.filter(Events.eventtype=="Lockdown").all()

    return render_template("entryvehiclebydate.html" , user=current_user, events=all_events)

@screen.route('/entryvehicletoday')
@login_required
def entrybydatetoday():
    GMT = pytz.timezone('Singapore')
    now = datetime.now(GMT)
    datetimeformat = datetime.strftime(now,"%Y-%m-%d")
    today_entry = EntryVehicle.query.filter(EntryVehicle.datetime.contains(datetimeformat)).join(User, EntryVehicle.email == User.id).all()

    datetimeshow = datetime.strftime(now,"%d-%m-%Y")
    return render_template("entryvehiclebytoday.html" , user=current_user, entry=today_entry, datetime = datetimeshow)

@screen.route('/entryvehiclebydatepost,<id>')
@login_required
def entrybydatepost(id):
    event = Events.query.filter_by(id = id).first()
    startdatetimeformat = event.startdate.strftime("%Y-%m-%d")
    enddatetimeformat = event.enddate.strftime("%Y-%m-%d")

    entryvehicle = EntryVehicle.query.filter(EntryVehicle.datetime.between(startdatetimeformat, enddatetimeformat)).join(User, EntryVehicle.email == User.id)


    return render_template("entryvehicledatepost.html", user = current_user, event=event, entryvehicle=entryvehicle)





