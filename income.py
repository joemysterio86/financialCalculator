from models import Income, last_of_month, this_month
import os, time
import sqlalchemy as db
from sqlalchemy import func
from sqlalchemy.orm import session, sessionmaker
from dateutil import rrule
from dateutil.parser import parse

db_path = os.path.join(os.getcwd(), 'main.db')
db_uri = 'sqlite:///{}'.format(db_path)
engine = db.create_engine(db_uri)
metadata = db.MetaData()
Session = sessionmaker(bind=engine)
session = Session()

def insert_income(*args):
    insert = Income(
        user=args[0],
        base_income_amount=args[1],
        actual_income_amount=args[1],
        pay_day=args[2],
        pay_day_frequency=args[3]
        )
    session.add(insert)
    session.commit()

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
            insert_income(args[0], args[1], x.date(), args[3])

def add_income():
    sched_options = ["weekly","biweekly","bimonthly","monthly"]
    while True:
        inc_belong = input("\nPlease enter who this income belongs to: ")
        if inc_belong == "":
            continue
        else:
            break
    while True:
        inc_amount = input("Please enter paycheck amount: ")
        if inc_amount == "":
            continue
        else:
            break
    while True:
        inc_date1 = parse(input("Please enter next expected pay date (YYYY-MM-DD) : "))
        if inc_date1 == "":
            continue
        else:
            break
    while True:
        inc_sched = input("Please indicate if pay schedule is weekly, biweekly, bimonthly, or monthly: ")
        if inc_sched not in sched_options:
            continue
        else:
            break
    rrule_date = str(inc_date1.date()).replace('-','')
    if inc_sched == "bimonthly":
        inc_date2 = parse(input("You selected bimonthly, what is the 2nd expected pay date (YYYY-MM-DD) : "))
        print("Thanks, adding income to the database...")
        insert_income(inc_belong, inc_amount, inc_date1, inc_sched)
        insert_income(inc_belong, inc_amount, inc_date2, inc_sched)
    elif inc_sched == "monthly":
        print("Thanks, adding income to the database...")
        insert_income(inc_belong, inc_amount, inc_date1, inc_sched)
    else:
        rr_pay_days(inc_belong, inc_amount, rrule_date, inc_sched)
    print("\n\nIncome added for entire month! Taking you back to Income Menu.\n")
    time.sleep(1)

def update_income():
    while True:
        vyi = session.query(Income.id, Income.user, Income.base_income_amount, Income.actual_income_amount, func.date(Income.pay_day), Income.pay_day_frequency).filter(Income.pay_day.between(this_month.date(),last_of_month.date())).order_by(Income.pay_day)
        formatted_result = [f"{id:<6}{user:<15}{base_income_amount:<12}{actual_income_amount:<16}{pay_day:<16}{pay_day_frequency:<15}" for id, user, base_income_amount, actual_income_amount, pay_day, pay_day_frequency in vyi]
        id, user, base_income_amount, actual_income_amount, pay_day, pay_day_frequency = "ID#", "User", "Base Pay", "Payday Amount", "Payday Start", "Payday Frequency"
        print("\n\nYour Income:\n")
        print('\n'.join([f"{id:<6}{user:<15}{base_income_amount:<12}{actual_income_amount:<16}{pay_day:<16}{pay_day_frequency:<15}"] + formatted_result))

        id_list = [id for (id,) in session.query(Income.id).order_by(Income.id)]
        inc_update_choice = input("\nPlease enter an ID to update, R to return to Income Menu, or Q to return to Main Menu: ")
        if inc_update_choice.lower() == "q":
            return
        elif inc_update_choice.lower() == "r":
            break
        elif int(inc_update_choice) in id_list:
            # inc_upd_base = input("")
            print("stuff form ID")
        else:
            print("\nPlease select an appropriate option!")
            time.sleep(0.5)

def income_questions():
    while True:
        vyi = session.query(Income.user, Income.actual_income_amount, func.date(Income.pay_day), Income.pay_day_frequency).filter(Income.pay_day.between(this_month.date(),last_of_month.date())).order_by(Income.pay_day)
        formatted_result = [f"{user:<15}{actual_income_amount:<16}{pay_day:<16}{pay_day_frequency:<15}" for user, actual_income_amount, pay_day, pay_day_frequency in vyi]
        user, actual_income_amount, pay_day, pay_day_frequency = "User", "Payday Amount", "Payday Start", "Payday Frequency"
        print("\n\nYour Income:\n")
        print('\n'.join([f"{user:<15}{actual_income_amount:<16}{pay_day:<16}{pay_day_frequency:<15}"] + formatted_result))

        inc_choices = input("""\n\nPress ENTER key to continue to main menu, or selection one of the following:
            
            1) Add Income.
            2) Update Income.
            3) Delete Income.
            
""")

        if inc_choices == "":
            return
        elif inc_choices == "1":
            add_income()
        elif inc_choices == "2":
            update_income()
        elif inc_choices == "3":
            pass

        else:
            print("Please hit ENTER to return to main menu, or select one of other options!")
            time.sleep(0.5)

