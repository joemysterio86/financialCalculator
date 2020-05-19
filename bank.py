from models import Bank
import os, time, datetime, calendar, sqlite3
import sqlalchemy as db
from sqlalchemy import cast, func, Column, Integer, String, DATETIME, REAL, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import session, sessionmaker
from dateutil import rrule
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

db_path = os.path.join(os.getcwd(), 'main.db')
db_uri = 'sqlite:///{}'.format(db_path)
engine = db.create_engine(db_uri)
metadata = db.MetaData()
Session = sessionmaker(bind=engine)
session = Session()

def view_your_bank():
    pass
