import os, time, datetime, calendar, sqlite3
import sqlalchemy as db
from sqlalchemy import cast, func, Column, Integer, String, DATETIME, REAL, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import session, sessionmaker
from dateutil import rrule
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

date_today = datetime.datetime.today()
rr_month = rrule.rrulestr('DTSTART:20200101\nRRULE:BYMONTHDAY=1;INTERVAL=1;FREQ=MONTHLY;UNTIL=20500101')
this_month = date_today.replace(day=1,hour=0,minute=0,second=0,microsecond=0)
last_of_month = rr_month.after(this_month) - datetime.timedelta(days=1)

db_path = os.path.join(os.getcwd(), 'main.db')
db_uri = 'sqlite:///{}'.format(db_path)
engine = db.create_engine(db_uri)
metadata = db.MetaData()
Session = sessionmaker(bind=engine)
session = Session()

def view_your_bank():
    from main import Bank
    pass
