from models import Income, db_uri, last_of_month, this_month, next_month
import os, time
import sqlalchemy as db
from sqlalchemy import func
from sqlalchemy.orm import session, sessionmaker
from dateutil import rrule
from dateutil.parser import parse

engine = db.create_engine(db_uri)
metadata = db.MetaData()
Session = sessionmaker(bind=engine)
session = Session()

def add_income(*args):
    add = Income(
        user=args[0],
        base_income_amount=args[1],
        actual_income_amount=args[1],
        pay_day=args[2],
        pay_day_frequency=args[3]
        )
    session.add(add)

def update_income(id, col, val):
    session.query(Income).filter(Income.id == id).update({col: val})

def delete_income(id):
    session.query(Income).filter(Income.id == id).delete()

# This function will take what's generated as "rr", an rrulestr, for the amount of times there's a pay date,
# cycles through each date, and insert it in DB as income. Mainly for weekly/biweekly schedule.
def rr_pay_days(*args):
    lam = str(last_of_month.date()).replace('-','')
    if args[3].lower() == "weekly":
        weekly = f"BYDAY=FR;INTERVAL=1;FREQ=WEEKLY;UNTIL={lam}"
        rr = rrule.rrulestr(f"DTSTART:{args[2]}\nRRULE:{weekly}")
    elif args[3].lower() == "biweekly":
        biweekly = f"BYDAY=FR;INTERVAL=2;FREQ=WEEKLY;UNTIL={lam}"
        rr = rrule.rrulestr(f"DTSTART:{args[2]}\nRRULE:{biweekly}")
    for x in rr:
        if this_month <= x <= last_of_month:
            add_income(args[0], args[1], x.date(), args[3])
            time.sleep(0.1)

def add_income_menu():
    sched_options = ["weekly","biweekly","bimonthly","monthly","one-time","q"]
    print("Press Q if you need to cancel and return to previous menu.\n")
    while True:
        inc_belong = input("Please enter who this income belongs to: ")
        if inc_belong == "":
            continue
        elif inc_belong.lower() == "q":
            return
        else:
            break
    while True:
        inc_amount = input("Please enter paycheck amount: ")
        if inc_amount == "":
            continue
        elif inc_amount.lower() == "q":
            return
        else:
            break
    while True:
        inc_date1 = input("Please enter next expected pay date (YYYY-MM-DD) : ")
        if inc_date1 == "":
            continue
        elif inc_date1.lower() == "q":
            return
        else:
            break
    while True:
        inc_sched = input("Please indicate if pay schedule is weekly, biweekly, bimonthly, monthly, or one-time: ")
        if inc_sched not in sched_options:
            continue
        elif inc_sched.lower() == "q":
            return
        else:
            break
    rrule_date = str(parse(inc_date1).date()).replace('-','')
    if inc_sched == "bimonthly":
        inc_date2 = input("You selected bimonthly, what is the 2nd expected pay date (YYYY-MM-DD) : ")
        print("Thanks, adding income to the database...")
        add_income(inc_belong, inc_amount, parse(inc_date1), inc_sched)
        add_income(inc_belong, inc_amount, parse(inc_date2), inc_sched)
    elif inc_sched == "monthly":
        print("Thanks, adding income to the database...")
        add_income(inc_belong, inc_amount, parse(inc_date1), inc_sched)
    elif inc_sched == "one-time":
        print("Thanks, adding income to the database...")
        add_income(inc_belong, inc_amount, parse(inc_date1), inc_sched)
    else:
        rr_pay_days(inc_belong, inc_amount, rrule_date, inc_sched)
    session.commit()
    print("Income added for entire month! Taking you back to Income Menu.\n")
    time.sleep(1)

def update_income_menu():
    while True:
        vyi = session.query(Income.id, Income.user, Income.base_income_amount, Income.actual_income_amount, func.date(Income.pay_day), Income.pay_day_frequency).filter(Income.pay_day.between(this_month.date(),next_month.date())).order_by(Income.pay_day)
        formatted_result = [f"{id:<6}{user:<15}{base_income_amount:<12}{actual_income_amount:<16}{pay_day:<16}{pay_day_frequency:<15}" for id, user, base_income_amount, actual_income_amount, pay_day, pay_day_frequency in vyi]
        id, user, base_income_amount, actual_income_amount, pay_day, pay_day_frequency = "ID#", "User", "Base Pay", "Payday Amount", "Pay Day", "Payday Frequency"
        print("\n\nYour Income:\n")
        print('\n'.join([f"{id:<6}{user:<15}{base_income_amount:<12}{actual_income_amount:<16}{pay_day:<16}{pay_day_frequency:<15}"] + formatted_result))

        id_list = [id for (id,) in session.query(Income.id).order_by(Income.id)]
        while True:
            inc_update_choice = input("\n\nPlease enter an ID to update, or Q to return to previous menu: ")
            if inc_update_choice.lower() == "":
                break
            elif inc_update_choice.lower() == "q":
                return
            elif inc_update_choice in str(id_list):
                while True:
                    vyi = session.query(Income.id, Income.user, Income.base_income_amount, Income.actual_income_amount, func.date(Income.pay_day), Income.pay_day_frequency).filter(Income.pay_day.between(this_month.date(),next_month.date())).filter(Income.id == float(inc_update_choice))
                    formatted_result = [f"{id:<6}{user:<15}{base_income_amount:<12}{actual_income_amount:<16}{pay_day:<16}{pay_day_frequency:<15}" for id, user, base_income_amount, actual_income_amount, pay_day, pay_day_frequency in vyi]
                    id, user, base_income_amount, actual_income_amount, pay_day, pay_day_frequency = "ID#", "User", "Base Pay", "Pay Day Amount", "Pay Day", "Pay Day Frequency"
                    print("\n\nYour Income:\n")
                    print('\n'.join([f"{id:<6}{user:<15}{base_income_amount:<12}{actual_income_amount:<16}{pay_day:<16}{pay_day_frequency:<15}"] + formatted_result))

                    iuc = input("""

Update Menu:

    1) Base Pay Amount
    2) Pay Day Amount
    3) Pay Day
    4) Pay Day Frequency
    Q) Return to previous menu


Please select an option: """)
                    if iuc.lower() == "q":
                        break
                    elif iuc == "1":
                        while True:
                            inc_upd = input("Please enter new value for Base Pay Amount or Q to cancel: ")
                            if inc_upd == "":
                                continue
                            elif inc_upd == "q":
                                break
                            else:
                                update_income(float(inc_update_choice), "base_income_amount", inc_upd)
                                session.commit()
                                print("Updated!!")
                                time.sleep(0.5)
                                break
                    elif iuc == "2":
                        while True:
                            inc_upd = input("Please enter new value for Pay Day Amount or Q to cancel: ")
                            if inc_upd == "":
                                continue
                            elif inc_upd == "q":
                                break
                            else:
                                update_income(float(inc_update_choice), "actual_income_amount", inc_upd)
                                session.commit()
                                print("Entry has been update.")
                                time.sleep(0.5)
                                break
                    elif iuc == "3":
                        while True:
                            inc_upd = input("Please enter new value for Pay Day Date (YYYY-MM-DD) or Q to cancel: ")
                            if inc_upd == "":
                                continue
                            elif inc_upd == "q":
                                break
                            else:
                                update_income(float(inc_update_choice), "pay_day", parse(inc_upd))
                                session.commit()
                                print("Entry has been update.")
                                time.sleep(0.5)
                                break
                    elif iuc == "4":
                        while True:
                            sched_options = ["weekly","biweekly","bimonthly","monthly","one-time","q"]
                            inc_upd = input("Options: weekly, biweekly, bimonthly, monthly, or one-time\n\nPlease enter new value for Pay Day Frequency or Q to cancel: ")
                            if inc_upd not in sched_options:
                                continue
                            elif inc_upd == "q":
                                break
                            else:
                                update_income(float(inc_update_choice), "pay_day_frequency", inc_upd)
                                session.commit()
                                print("Entry has been update.")
                                time.sleep(0.5)
                                break
                    else:
                        print("Please select one of the four options or (Q)uit:\n")
                        continue
                break
            else:
                break

def delete_income_menu():
    while True:
        vyi = session.query(Income.id, Income.user, Income.base_income_amount, Income.actual_income_amount, func.date(Income.pay_day), Income.pay_day_frequency).filter(Income.pay_day.between(this_month.date(),next_month.date())).order_by(Income.pay_day)
        formatted_result = [f"{id:<6}{user:<15}{base_income_amount:<12}{actual_income_amount:<16}{pay_day:<16}{pay_day_frequency:<15}" for id, user, base_income_amount, actual_income_amount, pay_day, pay_day_frequency in vyi]
        id, user, base_income_amount, actual_income_amount, pay_day, pay_day_frequency = "ID#", "User", "Base Pay", "Payday Amount", "Pay Day", "Payday Frequency"
        print("\n\nYour Income:\n")
        print('\n'.join([f"{id:<6}{user:<15}{base_income_amount:<12}{actual_income_amount:<16}{pay_day:<16}{pay_day_frequency:<15}"] + formatted_result))

        id_list = [id for (id,) in session.query(Income.id).order_by(Income.id)]
        while True:
            inc_delete_choice = input("\n\nPlease enter an ID to delete, or Q to return to previous menu: ")
            if inc_delete_choice.lower() == "":
                break
            elif inc_delete_choice.lower() == "q":
                return
            elif inc_delete_choice in str(id_list):
                delete_income(inc_delete_choice)
                session.commit()
                print("Entry has been removed.")
                time.sleep(0.5)
                break
            else:
                break

def income_questions():
    while True:
        vyi = session.query(Income.user, Income.actual_income_amount, func.date(Income.pay_day), Income.pay_day_frequency).filter(Income.pay_day.between(this_month.date(),next_month.date())).order_by(Income.pay_day)
        formatted_result = [f"{user:<15}{actual_income_amount:<16}{pay_day:<16}{pay_day_frequency:<15}" for user, actual_income_amount, pay_day, pay_day_frequency in vyi]
        user, actual_income_amount, pay_day, pay_day_frequency = "User", "Payday Amount", "Pay Day", "Payday Frequency"
        print("\n\nYour Income:\n")
        print('\n'.join([f"{user:<15}{actual_income_amount:<16}{pay_day:<16}{pay_day_frequency:<15}"] + formatted_result))

        inc_choices = input("""

Income Menu:

    1) Add Income.
    2) Update Income.
    3) Delete Income.
    Q) Return to Main Menu.


Please select an option: """)

        if inc_choices == "":
            continue
        elif inc_choices.lower() == "q":
            return
        elif inc_choices == "1":
            add_income_menu()
        elif inc_choices == "2":
            update_income_menu()
        elif inc_choices == "3":
            delete_income_menu()
        else:
            print("Please hit ENTER to return to main menu, or select one of other options!")
            time.sleep(0.5)

