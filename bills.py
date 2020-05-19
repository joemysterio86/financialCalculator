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

# next_bill is to show you today's date along with what is and how much your next bill will be.
def next_bill():
    from main import Bills 
    bill = session.query(Bills.bill_name, Bills.base_amount_due).filter(Bills.due_date >= date_today).first()
    if bill:
        print(f"""Today's date is: {date_today.date()}
Your next bill is {bill[0].upper()} for the amount of {bill[1]}.
""")
    else:
        print(f"Today's date is: {date_today.date()}")


def insert_bill(*args):
    from main import Bills 
    insert = Bills(
        bill_name=args[0],
        base_amount_due=args[1],
        actual_amount_due=args[2],
        due_date=args[3]
        )
    session.add(insert)
    session.commit()

def view_your_bills():
    from main import Bills 
    vyb = session.query(Bills.bill_name, Bills.base_amount_due, Bills.actual_amount_due, func.date(Bills.due_date)).order_by(Bills.due_date)
    formatted_result = [f"{bill_name:<20}{base_amount_due:<14}{actual_amount_due:<14}{due_date:<15}" for bill_name, base_amount_due, actual_amount_due, due_date in vyb]
    bill_name, base_amount_due, actual_amount_due, due_date = "Bill", "Monthly Due", "Current Due", "Due Date"
    print("\n\nYour Bills:\n")
    print('\n'.join([f"{bill_name:<20}{base_amount_due:<14}{actual_amount_due:<14}{due_date:<15}"] + formatted_result))

def bill_questions():
    from main import Bills 
    while True:
        bill1 = input("\nPlease enter the bill name: ")
        if bill1 == "":
            continue
        else:
            break
    while True:
        bill2 = input("Please enter what is normally due: ")
        if bill2 == "":
            continue
        else:
            break
    while True:
        bill3 = input("Please enter what you will pay: ")
        if bill3 == "":
            continue
        else:
            break
    while True:
        bill4 = parse(input("Please enter the bill due date (YYYY-MM-DD): "))
        if bill4 == "":
            continue
        else:
            break
    print("Thanks, creating this bill...")
    time.sleep(.5)
    insert_bill(bill1, bill2, bill3, bill4)
    print("\n\nBill created! Taking you back to main menu.\n")
    time.sleep(1)

