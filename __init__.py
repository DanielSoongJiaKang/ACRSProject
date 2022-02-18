from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
import os
from flask_login import LoginManager
from flask_mail import Mail


db = SQLAlchemy()
DB_NAME = "ACRSProject$ACRSDB"
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'ACRSFYPProject'
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://ACRSProject:Password...12345@ACRSProject.mysql.pythonanywhere-services.com/ACRSProject$ACRSDB"
    app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'acrsfyproject@gmail.com'
    app.config['MAIL_PASSWORD'] = 'Password...12345'
    Mail(app)


    from .views import views
    from .auth import auth
    from .report import reports
    from .userlist import userlist
    from .vehiclescreen import screen
    from .vehicle import vehicle
    from .illegalpark import illegalpark
    from .account import account
    from .viewlist import viewlist
    from .appeal import appeal
    from .useraudit import useraudit


    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(reports, url_prefix='/')
    app.register_blueprint(screen, url_prefix='/')
    app.register_blueprint(userlist, url_prefix='/')
    app.register_blueprint(vehicle, url_prefix='/')
    app.register_blueprint(illegalpark, url_prefix='/')
    app.register_blueprint(illegalpark, url_prefix='/')
    app.register_blueprint(account, url_prefix='/')
    app.register_blueprint(viewlist, url_prefix='/')
    app.register_blueprint(appeal, url_prefix='/')
    app.register_blueprint(useraudit, url_prefix='/')



    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/uploads/')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    from .models import User

    create_database(app)


    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))







    return app



def create_database(app):
    if not path.exists('ACRS/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')