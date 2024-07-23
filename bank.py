from models import Bank, db_uri
import os, time, datetime, calendar, sqlite3
import sqlalchemy as db
from sqlalchemy import cast, func, Column, Integer, String, DATETIME, REAL, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import session, sessionmaker
from dateutil import rrule
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

engine = db.create_engine(db_uri)
metadata = db.MetaData()
Session = sessionmaker(bind=engine)
session = Session()

def add_bank(*args):
    add = Bank(
        bank_name=args[0],
        checkings_total=args[1],
        savings_total=args[2],
        )
    session.add(add)

def update_bank(id, col, val):
    session.query(Bank).filter(Bank.id == id).update({col: val})

def delete_bank(id):
    session.query(Bank).filter(Bank.id == id).delete()


def add_bank_menu():
    print("Press Q if you need to cancel and return to previous menu.\n")
    while True:
        bank1 = input("Please enter the name of the bank: ")
        if bank1 == "":
            continue
        elif bank1.lower() == "q":
            return
        else:
            break
    while True:
        bank2 = input("(Enter 0 if no checkings account available here)\nPlease enter Checkings Account balance: ")
        if bank2 == "":
            continue
        elif bank2.lower() == "q":
            return
        else:
            break
    while True:
        bank3 = input("(Enter 0 if no savings account available here)\nPlease enter Savings Account balance: ")
        if bank3 == "":
            continue
        elif bank3.lower() == "q":
            return
        else:
            break
    add_bank(bank1, float(bank2), float(bank3))
    session.commit()
    print("Bank info has been added. Taking you back to Bank Menu.\n")
    time.sleep(1)

def update_bank_menu():
    while True:
        vybank = session.query(Bank.id, Bank.bank_name, Bank.checkings_total, Bank.savings_total).order_by(Bank.bank_name)
        formatted_result = [f"{id:<6}{bank_name:<20}{checkings_total:<16}{savings_total:<16}" for id, bank_name, checkings_total, savings_total in vybank]
        id, bank_name, checkings_total, savings_total = "ID#", "Bank Name", "Checkings Total", "Savings Total"
        print("\n\nYour Bank(s):\n")
        print('\n'.join([f"{id:<6}{bank_name:<20}{checkings_total:<16}{savings_total:<16}"] + formatted_result))

        id_list = [id for (id,) in session.query(Bank.id).order_by(Bank.id)]
        while True:
            bank_update_choice = input("\n\nPlease enter an ID to update, or Q to return to previous menu: ")
            if bank_update_choice.lower() == "":
                break
            elif bank_update_choice.lower() == "q":
                return
            elif bank_update_choice in str(id_list):
                while True:
                    vybank = session.query(Bank.id, Bank.bank_name, Bank.checkings_total, Bank.savings_total).order_by(Bank.bank_name).filter(Bank.id == float(bank_update_choice))
                    formatted_result = [f"{id:<6}{bank_name:<20}{checkings_total:<16}{savings_total:<16}" for id, bank_name, checkings_total, savings_total in vybank]
                    id, bank_name, checkings_total, savings_total = "ID#", "Bank Name", "Checkings Total", "Savings Total"
                    print("\n\nYour Bank(s):\n")
                    print('\n'.join([f"{id:<6}{bank_name:<20}{checkings_total:<16}{savings_total:<16}"] + formatted_result))

                    bauc = input("""

Update Menu:

    1) Checkings Total
    2) Savings Total
    Q) Return to previous menu


Please select an option: """)
                    if bauc.lower() == "q":
                        break
                    elif bauc == "1":
                        while True:
                            bank_upd = input("Please enter new value for Checkings Total or Q to cancel: ")
                            if bank_upd == "":
                                continue
                            elif bank_upd == "q":
                                break
                            else:
                                update_bank(float(bank_update_choice), "checkings_total", bank_upd)
                                session.commit()
                                print("Updated!!")
                                time.sleep(0.5)
                                break
                    elif bauc == "2":
                        while True:
                            bank_upd = input("Please enter new value for Savings Total or Q to cancel: ")
                            if bank_upd == "":
                                continue
                            elif bank_upd == "q":
                                break
                            else:
                                update_bank(float(bank_update_choice), "savings_total", bank_upd)
                                session.commit()
                                print("Entry has been updated.")
                                time.sleep(0.5)
                                break
                    else:
                        print("Please select one of the two options or (Q)uit:\n")
                        continue
                break
            else:
                break

def delete_bank_menu():
    while True:
        vybank = session.query(Bank.id, Bank.bank_name, Bank.checkings_total, Bank.savings_total).order_by(Bank.bank_name)
        formatted_result = [f"{id:<6}{bank_name:<20}{checkings_total:<16}{savings_total:<16}" for id, bank_name, checkings_total, savings_total in vybank]
        id, bank_name, checkings_total, savings_total = "ID#", "Bank Name", "Checkings Total", "Savings Total"
        print("\n\nYour Bank(s):\n")
        print('\n'.join([f"{id:<6}{bank_name:<20}{checkings_total:<16}{savings_total:<16}"] + formatted_result))

        id_list = [id for (id,) in session.query(Bank.id).order_by(Bank.id)]
        while True:
            bank_delete_choice = input("\n\nPlease enter an ID to delete, or Q to return to previous menu: ")
            if bank_delete_choice.lower() == "":
                break
            elif bank_delete_choice.lower() == "q":
                return
            elif bank_delete_choice in str(id_list):
                delete_bank(bank_delete_choice)
                session.commit()
                print("Entry has been removed.")
                time.sleep(0.5)
                break
            else:
                break

def bank_questions():
    while True:
        vybank = session.query(Bank.bank_name, Bank.checkings_total, Bank.savings_total).order_by(Bank.bank_name)
        formatted_result = [f"{bank_name:<20}{checkings_total:<16}{savings_total:<16}" for bank_name, checkings_total, savings_total in vybank]
        bank_name, checkings_total, savings_total = "Bank Name", "Checkings Total", "Savings Total"
        print("\n\nYour Bank(s):\n")
        print('\n'.join([f"{bank_name:<20}{checkings_total:<16}{savings_total:<16}"] + formatted_result))

        ban_choices = input("""

Bank Menu:

    1) Add Bank.
    2) Update Bank.
    3) Delete Bank.
    Q) Return to Main Menu.


Please select an option: """)

        if ban_choices == "":
            continue
        elif ban_choices.lower() == "q":
            return
        elif ban_choices == "1":
            add_bank_menu()
        elif ban_choices == "2":
            update_bank_menu()
        elif ban_choices == "3":
            delete_bank_menu()
        else:
            print("Please hit ENTER to return to main menu, or select one of other options!")
            time.sleep(0.5)