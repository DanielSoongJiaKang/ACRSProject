from flask import Blueprint, render_template, request, flash, redirect, url_for,current_app
from .models import Vehicle, UserAudit
from . import db
from flask_login import login_required, current_user
from functools import wraps
import pandas as pd
import os
import pytz
from datetime import datetime


vehicle = Blueprint('vehicle', __name__)

class vehiclelist:
    def __init__(self, vehiclenop, holdernamep, holdertypep, carmakep, companyp):
        self.vehiclenop = vehiclenop
        self.holdernamep = holdernamep
        self.holdertypep = holdertypep
        self.carmakep = carmakep
        self.companyp = companyp


def admin_required(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if current_user.roles != "Admin":
                flash("You don't have permission to access this resource.", "warning")
                return redirect(url_for("views.home"))
            return func(*args, **kwargs)
        return decorated_view



@vehicle.route('/vehicle')
@login_required
@admin_required
def Index():
    all_data = Vehicle.query
    return render_template("vehicle.html", Vehicle = all_data, user=current_user)

@vehicle.route('/vehiclecreate', methods = ['GET','POST'])
@login_required
@admin_required
def insert():

    if request.method == 'POST':
        vehicleno = request.form['vehiclereg']
        holdername = request.form['hnamereg']
        holdertype = request.form['htypereg']
        model = request.form['modelreg']
        company = request.form['companyreg']

        vehicle = Vehicle.query.filter_by(vehicleno=vehicleno).first()
        if vehicle:
            flash('Vehicle already exists' , category='error')
        elif len(vehicleno) <= 7 and len(vehicleno) > 8:
            flash('Vehicle number invalid' , category='error')
        elif len(holdername) <2:
            flash('Holder name must be more than 1 character' , category='error')
        elif len(model) < 2:
            flash('Vehicle model must be more than 1 character', category='error')
        elif len(company) <2:
            flash('Company name must be more than 1 character', category='error')
        else:
            my_data = Vehicle(vehicleno=vehicleno, holdername=holdername, holdertype=holdertype, model=model, company=company )
            GMT = pytz.timezone('Singapore')
            now = datetime.now(GMT)
            datetimeformat = datetime.strftime(now,"%Y-%m-%d %H:%M:%S")
            new_audit = UserAudit(datetime=datetimeformat, email=current_user.id, action="Create new Vehicle:" + vehicleno +  " in Vehicle Management")
            db.session.add(new_audit)
            db.session.add(my_data)

            db.session.commit()
            flash("Vehicle Inserted Successfully")
            return redirect(url_for('vehicle.Index'))


    return render_template("vehiclecreate.html", user=current_user)


@vehicle.route('/vehicleupdate', methods = ['GET', 'POST'])
@login_required
@admin_required
def update():

    if request.method == 'POST':
        my_data = Vehicle.query.get(request.form.get('id'))

        my_data.vehicleno = request.form['vehicleno']
        my_data.holdername = request.form['holdername']
        my_data.holdertype = request.form['holdertype']
        my_data.model = request.form['model']
        my_data.company = request.form['company']
        GMT = pytz.timezone('Singapore')
        now = datetime.now(GMT)
        datetimeformat = datetime.strftime(now,"%Y-%m-%d %H:%M:%S")
        new_audit = UserAudit(datetime=datetimeformat, email=current_user.id, action="Update in Vehicle Management Vehicle ID: " + str(my_data.id))
        db.session.add(new_audit)


        db.session.commit()
        flash("Vehicle Updated Successfully")

        return redirect(url_for('vehicle.Index'))

@vehicle.route('/vehicledelete', methods = ['GET', 'POST'])
@login_required
@admin_required
def deletevehicle():
    if request.method == 'POST':
        i = 0
        for getid in request.form.getlist('vehcheckbox'):
            db.session.execute("DELETE FROM vehicle WHERE id = {0}".format(getid))
            db.session.commit()
            i+=1
    GMT = pytz.timezone('Singapore')
    now = datetime.now(GMT)
    datetimeformat = datetime.strftime(now,"%Y-%m-%d %H:%M:%S")
    new_audit = UserAudit(datetime=datetimeformat, email=current_user.id, action="Multiple Delete in Vehicle Management rows affected " + str(i))
    db.session.add(new_audit)
    db.session.commit()
    flash('Successfully Deleted!')
    return redirect(url_for('vehicle.Index'))




ALLOWED_EXTENSIONS = set(['csv'])

    #check file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@vehicle.route('/importvehicle', methods = ['GET', 'POST'])
@login_required
@admin_required
def importvehicle():
    if request.method == 'POST':
        if 'excelfile' not in request.files:
            flash("No files are selected", category="error")
            return render_template('importvehicle.html', user=current_user)
        excel = request.files['excelfile']
        radio = request.form['choice']
        if excel.filename == '':
            flash("No Selected File", category="error")
            return render_template("importvehicle.html" , user=current_user)


        excel.save(os.path.join(current_app.config["UPLOAD_FOLDER"], excel.filename))
        filename_path = os.path.join(current_app.config["UPLOAD_FOLDER"], excel.filename)
        data = pd.read_csv(filename_path)
        data.head()
        vehiclein = []
        outcome = ""
        i = 0
        c = 0
        try:

            for col in data.columns:
                i += 1

            if i == 5:
                if radio == 'True':
                    db.session.query(Vehicle).delete()
                    db.session.commit()
                for i, row in data.iterrows():
                    if "," in str(row[0]) or " " in str(row[0]):
                        data2 = row[0].split(",")
                        data2.pop(1)
                        if "nan" in str(row[3]):
                            row[3] = "No Model"
                        if "nan" in str(row[4]):
                            row[4] = "No Company"
                        if "Republic Polytechnic" in str(row[4]):
                            row[4] = "RP"
                        if(data2[0] != ""):
                            if "/" in str(row[3]):
                                data3 = row[3].split(" / ")
                                data3.pop(1)
                                vehiclein.append(vehiclelist(data2[0], row[1],row[2],data3[0],row[4]))

                for i, row in data.iterrows():
                    if "," in str(row[0]) or " " in str(row[0]):
                        data2 = row[0].split(",")
                        data2.pop(0)
                        if "nan" in str(row[3]):
                            row[3] = "No Model"
                        if "nan" in str(row[4]):
                            row[4] = "No Company"
                        if "Republic Polytechnic" in str(row[4]):
                            row[4] = "RP"
                        if(data2[0] != ""):
                            if "/" in str(row[3]):
                                data3 = row[3].split(" / ")
                                data3.pop(0)
                                vehiclein.append(vehiclelist(data2[0], row[1],row[2],data3[0],row[4]))


                for i, row in data.iterrows():
                    flag = 0
                    if "," in str(row[0]) or "nan" in str(row[0]) or " " in str(row[0]):
                        flag = 1
                    if "nan" in str(row[3]):
                        row[3] = "No Model"
                    if "nan" in str(row[4]):
                        row[4] = "No Company"
                    if "Republic Polytechnic" in str(row[4]):
                        row[4] = "RP"
                    if not flag:
                        vehiclein.append(vehiclelist(row[0], row[1],row[2],row[3],row[4]))

                for row in vehiclein:
                    vehicle = Vehicle.query.filter_by(vehicleno=row.vehiclenop).first()
                    if vehicle:
                        outcome += str(row.vehiclenop) + ", "

                    else:
                        my_data = Vehicle(vehicleno=str(row.vehiclenop), holdername=str(row.holdernamep), holdertype=str(row.holdertypep), model=str(row.carmakep), company=str(row.companyp))
                        db.session.add(my_data)
                        c+=1
                flash( 'Vehicle existed: ' + outcome , category='error')
                GMT = pytz.timezone('Singapore')
                now = datetime.now(GMT)
                datetimeformat = datetime.strftime(now,"%Y-%m-%d %H:%M:%S")
                new_audit = UserAudit(datetime=datetimeformat, email=current_user.id, action="Import Excel in Vehicle Management rows affected " + str(c))
                db.session.add(new_audit)
                db.session.commit()
                flash("Vehicle Imported Successfully from CSV!")
                return redirect(url_for('vehicle.Index'))
            else:
                flash("Vehicle CSV file need to be 5 columns", category="error")



        except:
            flash("Could not read CSV file please try again", category="error")
            return render_template("importvehicle.html", user=current_user)








    return render_template("importvehicle.html" , user = current_user)

