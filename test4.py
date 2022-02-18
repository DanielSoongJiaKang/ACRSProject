from . import db
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy.sql import func
from sqlalchemy import create_engine, extract



engine = create_engine("mysql+mysqlconnector://ACRSProject:Password...12345@ACRSProject.mysql.pythonanywhere-services.com/ACRSProject$ACRSDB")
Session = sessionmaker(bind=engine)
session = Session()

events = session.query(Events).all();
print(events)