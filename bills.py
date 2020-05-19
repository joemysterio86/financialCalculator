from models import Bills, date_today
import os, time
import sqlalchemy as db
from sqlalchemy import func
from sqlalchemy.orm import session, sessionmaker
from dateutil.parser import parse

db_path = os.path.join(os.getcwd(), 'main.db')
db_uri = 'sqlite:///{}'.format(db_path)
engine = db.create_engine(db_uri)
metadata = db.MetaData()
Session = sessionmaker(bind=engine)
session = Session()

# next_bill is to show you today's date along with what is and how much your next bill will be.
def next_bill():
    bill = session.query(Bills.bill_name, Bills.base_amount_due).filter(Bills.due_date >= date_today).first()
    if bill:
        print(f"Today's date is: {date_today.date()}\nYour next bill is {bill[0].upper()} for the amount of {bill[1]}.\n")
    else:
        print(f"Today's date is: {date_today.date()}\nYou don't have a bill due! Please check your finances.\n")

def insert_bill(*args):
    insert = Bills(
        bill_name=args[0],
        base_amount_due=args[1],
        actual_amount_due=args[2],
        due_date=args[3]
        )
    session.add(insert)
    session.commit()

def view_your_bills():
    vyb = session.query(Bills.bill_name, Bills.base_amount_due, Bills.actual_amount_due, func.date(Bills.due_date)).order_by(Bills.due_date)
    formatted_result = [f"{bill_name:<20}{base_amount_due:<14}{actual_amount_due:<14}{due_date:<15}" for bill_name, base_amount_due, actual_amount_due, due_date in vyb]
    bill_name, base_amount_due, actual_amount_due, due_date = "Bill", "Monthly Due", "Current Due", "Due Date"
    print("\n\nYour Bills:\n")
    print('\n'.join([f"{bill_name:<20}{base_amount_due:<14}{actual_amount_due:<14}{due_date:<15}"] + formatted_result))

def bill_questions():
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

