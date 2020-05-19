import os, datetime
from dateutil import rrule
import sqlalchemy as db
from sqlalchemy import Column, Integer, String, DATETIME, REAL
from sqlalchemy.ext.declarative import declarative_base

date_today = datetime.datetime.today()
this_month = date_today.replace(day=1,hour=0,minute=0,second=0,microsecond=0)
rr_month = rrule.rrulestr('DTSTART:20200101\nRRULE:BYMONTHDAY=1;INTERVAL=1;FREQ=MONTHLY;UNTIL=20500101')
last_of_month = rr_month.after(this_month) - datetime.timedelta(days=1)

db_path = os.path.join(os.getcwd(), 'main.db')
db_uri = 'sqlite:///{}'.format(db_path)
engine = db.create_engine(db_uri)
metadata = db.MetaData()
Base = declarative_base()

class Income(Base):
    __tablename__ = 'income'
    id = Column(Integer, primary_key=True)
    user = Column(String)
    base_income_amount = Column(REAL)
    actual_income_amount = Column(REAL)
    pay_day = Column(DATETIME)
    pay_day_frequency = Column(String)
    def __repr__(self):
        return f'ID: {self.id}, User Name: {self.user}, Base Income Amount: {self.base_income_amount}, Actual Income Amount: {self.actual_income_amount}, Pay Day: {self.pay_day}, Pay Day Frequency: {self.pay_day_frequency}'

class Bills(Base):
    __tablename__ = 'bills'
    id = Column(Integer, primary_key=True)
    bill_name = Column(String)
    base_amount_due = Column(REAL)
    actual_amount_due = Column(REAL)
    due_date = Column(DATETIME)
    def __repr__(self):
        return f'ID: {self.id}, Bill Name: {self.bill_name}, Base Amount Due: {self.base_amount_due}, Actual Amount Due: {self.actual_amount_due}, Due Date: {self.due_date}'

class Bank(Base):
    __tablename__ = 'bank'
    id = Column(Integer, primary_key=True)
    bank = Column(String)
    total = Column(REAL)
    def __repr__(self):
        return f'ID: {self.id}, Bank Name: {self.bank}, Bank Total: {self.total}'

class Month(Base):
    __tablename__ = 'month'
    id = Column(Integer, primary_key=True)
    month = Column(String)
    def __repr__(self):
        return f'ID: {self.id}, Month: {self.bank}'

Base.metadata.create_all(engine)

engine.execute("CREATE VIEW IF NOT EXISTS all_entries as SELECT bill_name, actual_amount_due, due_date FROM bills union SELECT user, actual_income_amount, pay_day FROM income;")
all_entries = db.Table('all_entries', metadata, autoload=True, autoload_with=engine)
