from models import Bills, db_uri, date_today, this_month, next_month
import os, time
import sqlalchemy as db
from sqlalchemy import func
from sqlalchemy.orm import session, sessionmaker
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta


engine = db.create_engine(db_uri)
metadata = db.MetaData()
Session = sessionmaker(bind=engine)
session = Session()

# next_bill is to show you today's date along with what is and how much your next bill will be.
def next_bill():
    bill = session.query(Bills.bill_name, Bills.base_amount_due, Bills.due_date).filter(Bills.due_date >= date_today - relativedelta(days=+1)).order_by(Bills.due_date).first()
    if bill:
        print(f"Today's date is: {date_today.date()}\nYour next bill is {bill[0].upper()} for the amount of {bill[1]} on {bill[2].date()}.\n")
    else:
        print(f"Today's date is: {date_today.date()}\nYou don't have a bill due! Please check your finances.\n")

def add_bills(*args):
    add = Bills(
        bill_name=args[0],
        base_amount_due=args[1],
        actual_amount_due=args[2],
        due_date=args[3]
        )
    session.add(add)
    session.commit()

def update_bills(id, col, val):
    session.query(Bills).filter(Bills.id == id).update({col: val})
    session.commit()

def delete_bills(id):
    session.query(Bills).filter(Bills.id == id).delete()
    session.commit()

def add_bills_menu():
    print("Press Q if you need to cancel and return to previous menu.\n")
    while True:
        bill1 = input("\nPlease enter the bill name: ")
        if bill1 == "":
            continue
        elif bill1.lower() == "q":
            return
        else:
            break
    while True:
        bill2 = input("Please enter what is normally due: ")
        if bill2 == "":
            continue
        elif bill2.lower() == "q":
            return
        else:
            break
    while True:
        bill3 = input("Please enter what you will pay: ")
        if bill3 == "":
            continue
        elif bill3.lower() == "q":
            return
        else:
            break
    while True:
        bill4 = input("Please enter the bill due date (YYYY-MM-DD): ")
        if bill4 == "":
            continue
        elif bill4.lower() == "q":
            return
        else:
            break
    print("Thanks, creating this bill...")
    time.sleep(.5)
    add_bills(bill1, bill2, bill3, parse(bill4))
    print("\n\nBill created! Taking you back to Bills Menu.\n")
    time.sleep(1)

def update_bills_menu():
    while True:
        vyb = session.query(Bills.id, Bills.bill_name, Bills.base_amount_due, Bills.actual_amount_due, func.date(Bills.due_date)).filter(Bills.due_date.between(this_month.date(),next_month.date())).order_by(Bills.due_date)
        formatted_result = [f"{id:<6}{bill_name:<20}{base_amount_due:<14}{actual_amount_due:<14}{due_date:<15}" for id, bill_name, base_amount_due, actual_amount_due, due_date in vyb]
        id, bill_name, base_amount_due, actual_amount_due, due_date = "ID#", "Bill", "Monthly Due", "Current Due", "Due Date"
        print("\n\nYour Bills:\n")
        print('\n'.join([f"{id:<6}{bill_name:<20}{base_amount_due:<14}{actual_amount_due:<14}{due_date:<15}"] + formatted_result))

        id_list = [id for (id,) in session.query(Bills.id).order_by(Bills.id)]
        while True:
            bill_update_choice = input("\n\nPlease enter an ID to update, or Q to return to previous menu: ")
            if bill_update_choice.lower() == "":
                break
            elif bill_update_choice.lower() == "q":
                return
            elif bill_update_choice in str(id_list):
                while True:
                    vyb = session.query(Bills.id, Bills.bill_name, Bills.base_amount_due, Bills.actual_amount_due, func.date(Bills.due_date)).filter(Bills.due_date.between(this_month.date(),next_month.date())).filter(Bills.id == float(bill_update_choice))
                    formatted_result = [f"{id:<6}{bill_name:<20}{base_amount_due:<14}{actual_amount_due:<14}{due_date:<15}" for id, bill_name, base_amount_due, actual_amount_due, due_date in vyb]
                    id, bill_name, base_amount_due, actual_amount_due, due_date = "ID#", "Bill", "Monthly Due", "Current Due", "Due Date"
                    print("\n\nYour Bills:\n")
                    print('\n'.join([f"{id:<6}{bill_name:<20}{base_amount_due:<14}{actual_amount_due:<14}{due_date:<15}"] + formatted_result))

                    buc = input("""

Update Menu:

    1) Base Amount Due
    2) Actual Amount Due
    3) Due Date
    Q) Return to previous menu


Please select an option: """)
                    if buc.lower() == "q":
                        break
                    elif buc == "1":
                        while True:
                            bill_upd = input("Please enter new value for Base Amount Due or Q to cancel: ")
                            if bill_upd == "":
                                continue
                            elif bill_upd == "q":
                                break
                            else:
                                update_bills(float(bill_update_choice), "base_amount_due", bill_upd)
                                print("Updated!!")
                                time.sleep(0.5)
                                break
                    elif buc == "2":
                        while True:
                            bill_upd = input("Please enter new value for Actual Amount Due or Q to cancel: ")
                            if bill_upd == "":
                                continue
                            elif bill_upd == "q":
                                break
                            else:
                                update_bills(float(bill_update_choice), "actual_amount_due", bill_upd)
                                print("Entry has been update.")
                                time.sleep(0.5)
                                break
                    elif buc == "3":
                        while True:
                            bill_upd = input("Please enter new value for Due Date (YYYY-MM-DD) or Q to cancel: ")
                            if bill_upd == "":
                                continue
                            elif bill_upd == "q":
                                break
                            else:
                                update_bills(float(bill_update_choice), "due_date", parse(bill_upd))
                                print("Entry has been update.")
                                time.sleep(0.5)
                                break
                    else:
                        print("Please select one of the three options or (Q)uit:\n")
                        continue
                break
            else:
                break

def delete_bills_menu():
    while True:
        vyb = session.query(Bills.id, Bills.bill_name, Bills.base_amount_due, Bills.actual_amount_due, func.date(Bills.due_date)).filter(Bills.due_date.between(this_month.date(),next_month.date())).order_by(Bills.due_date)
        formatted_result = [f"{id:<6}{bill_name:<20}{base_amount_due:<14}{actual_amount_due:<14}{due_date:<15}" for id, bill_name, base_amount_due, actual_amount_due, due_date in vyb]
        id, bill_name, base_amount_due, actual_amount_due, due_date = "ID#", "Bill", "Monthly Due", "Current Due", "Due Date"
        print("\n\nYour Bills:\n")
        print('\n'.join([f"{id:<6}{bill_name:<20}{base_amount_due:<14}{actual_amount_due:<14}{due_date:<15}"] + formatted_result))

        id_list = [id for (id,) in session.query(Bills.id).order_by(Bills.id)]
        while True:
            bil_delete_choice = input("\n\nPlease enter an ID to delete, or Q to return to previous menu: ")
            if bil_delete_choice.lower() == "":
                break
            elif bil_delete_choice.lower() == "q":
                return
            elif bil_delete_choice in str(id_list):
                delete_bills(bil_delete_choice)
                print("Entry has been removed.")
                time.sleep(0.5)
                break
            else:
                break


def bills_questions():
    while True:
        vyb = session.query(Bills.bill_name, Bills.base_amount_due, Bills.actual_amount_due, func.date(Bills.due_date)).order_by(Bills.due_date)
        formatted_result = [f"{bill_name:<20}{base_amount_due:<14}{actual_amount_due:<14}{due_date:<15}" for bill_name, base_amount_due, actual_amount_due, due_date in vyb]
        bill_name, base_amount_due, actual_amount_due, due_date = "Bill", "Monthly Due", "Current Due", "Due Date"
        print("\n\nYour Bills:\n")
        print('\n'.join([f"{bill_name:<20}{base_amount_due:<14}{actual_amount_due:<14}{due_date:<15}"] + formatted_result))

        bill_choices = input("""

Bills Menu:

    1) Add Bills.
    2) Update Bills.
    3) Delete Bills.
    Q) Return to Main Menu.


Please select an option: """)

        if bill_choices == "":
            continue
        elif bill_choices.lower() == "q":
            return
        elif bill_choices == "1":
            add_bills_menu()
        elif bill_choices == "2":
            update_bills_menu()
        elif bill_choices == "3":
            delete_bills_menu()
        else:
            print("Please hit ENTER to return to main menu, or select one of other options!")
            time.sleep(0.5)
