from income import income_questions
from bills import bill_questions, next_bill 
from bank import view_your_bank 
from other import check_month, view_all_entries
import os, time, datetime, calendar, sqlite3
import sqlalchemy as db
from sqlalchemy import cast, func, Column, Integer, String, DATETIME, REAL, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dateutil import rrule
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta


db_path = os.path.join(os.getcwd(), 'main.db')
db_uri = 'sqlite:///{}'.format(db_path)
engine = db.create_engine(db_uri)
metadata = db.MetaData()
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

class Bills(Base):
    __tablename__ = 'bills'
    id = Column(Integer, primary_key=True)
    bill_name = Column(String)
    base_amount_due = Column(REAL)
    actual_amount_due = Column(REAL)
    due_date = Column(DATETIME)
    def __repr__(self):
        return f'Bill Name: {self.bill_name}, Base Amount Due: {self.base_amount_due}, Actual Amount Due: {self.actual_amount_due}, Due Date: {self.due_date}'

class Income(Base):
    __tablename__ = 'income'
    id = Column(Integer, primary_key=True)
    user = Column(String)
    base_income_amount = Column(REAL)
    actual_income_amount = Column(REAL)
    pay_day = Column(DATETIME)
    pay_day_frequency = Column(String)
    def __repr__(self):
        return f'User Name: {self.user}, Base Income Amount: {self.base_income_amount}, Actual Income Amount: {self.actual_income_amount}, Pay Day: {self.pay_day}, Pay Day Frequency: {self.pay_day_frequency}'

class Bank(Base):
    __tablename__ = 'bank'
    id = Column(Integer, primary_key=True)
    bank = Column(String)
    total = Column(REAL)
    def __repr__(self):
        return f'Bank Name: {self.bank}, Bank Total: {self.total}'

class Month(Base):
    __tablename__ = 'month'
    id = Column(Integer, primary_key=True)
    month = Column(String)
    def __repr__(self):
        return f'Bank Name: {self.bank}'

engine.execute("CREATE VIEW IF NOT EXISTS all_entries as SELECT bill_name, actual_amount_due, due_date FROM bills union SELECT user, actual_income_amount, pay_day FROM income;")
all_entries = db.Table('all_entries', metadata, autoload=True, autoload_with=engine)
Base.metadata.create_all(engine)

# self explanatory
date_today = datetime.datetime.today()
this_month = date_today.replace(day=1,hour=0,minute=0,second=0,microsecond=0)
rr_month = rrule.rrulestr('DTSTART:20200101\nRRULE:BYMONTHDAY=1;INTERVAL=1;FREQ=MONTHLY;UNTIL=20500101')
last_of_month = rr_month.after(this_month) - datetime.timedelta(days=1)

def menu():
    while True:
        check_month()
        next_bill()
        print(f"""What would you like to do?

        1) View all entries.
        2) Bank:
            View/Add/Update/Delete
        3) Income:
            View/Add/Update/Delete
        4) Bills:
            View/Add/Update/Delete
        Q) Exit.

        """)
        choice = input("Please select an option: ")
        if choice.lower() == "q":
            print("You selected Q, exiting...")
            exit()
        elif choice == "1":
            view_all_entries()
        elif choice == "2":
            view_your_bank()
        elif choice == "3":
            income_questions()
        elif choice == "4":
            bill_questions()
        else:
            print("\nPlease select an appropriate option!")
            time.sleep(.5)

menu()
