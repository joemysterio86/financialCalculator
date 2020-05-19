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


# check_month is meant to re-initialize each month to zero if it's a new month.
def check_month():
    from main import Bills, Income, Month 
    from income import insert_income, rr_pay_days 

    # gets the difference in months to be used in relativedelta.
    def diff_month(d1, d2):
        return (d1.year - d2.year) * 12 + d1.month - d2.month
    
    # checks if month table is empty, then adds a month base month. 
    monthFetch = session.query(Month.month).order_by(db.desc(Month.month)).limit(1)
    if monthFetch.first() == None:
        m = Month(month=datetime.datetime(2020,1,1))
        session.add(m)
        session.commit()

    # checks the current month, if not, sets up a new month to be current, resets bills back to original amount due, and updates income to new/current month.
    monthFetch = session.query(Month.month).order_by(db.desc(Month.month)).limit(1)
    if monthFetch.first()[0] == str(this_month):
        print(f"Financial App!!\n\nWe are now in the month of {date_today.strftime('%B').upper()}.\n")
    else:
        print("New month started! Initializing...\n\n\n")
        m = Month(month=this_month)
        session.add(m)
        session.commit()
        
        # loops through all entries and sets the actual amount due back to the base amount, and increases the due date to the current month.
        # cur.execute("select id, due_date from bills;")
        for id, base_amount_due, due_date in session.query(Bills.id, Bills.base_amount_due, Bills.due_date):
            i = diff_month(date_today, due_date)
            newDate = due_date + relativedelta(months=+i)
            session.query(Bills).filter(Bills.id == id).update({Bills.due_date: newDate, Bills.actual_amount_due: base_amount_due})

        # loops through income table and updates/increases the pay day to the current month.
        a = session.query(Income.id, Income.user, Income.base_income_amount, Income.actual_income_amount, Income.pay_day, Income.pay_day_frequency).group_by(Income.user).\
            filter(or_(Income.pay_day_frequency=='biweekly', Income.pay_day_frequency=='weekly'))
        b = session.query(Income.id, Income.user, Income.base_income_amount, Income.actual_income_amount, Income.pay_day, Income.pay_day_frequency).\
            filter(or_(Income.pay_day_frequency=='bimonthly', Income.pay_day_frequency=='monthly'))

        for user, base_income_amount, actual_income_amount, pay_day, pay_day_frequency in a.union_all(b):
            if pay_day_frequency == 'weekly':
                rrule_date = str(pay_day).replace('-','')[:-9]
                rr_pay_days(user, base_income_amount, rrule_date, pay_day_frequency)
            elif pay_day_frequency == 'biweekly':
                rrule_date = str(pay_day).replace('-','')[:-9]
                rr_pay_days(user, base_income_amount, rrule_date, pay_day_frequency)
            else:
                i = diff_month(date_today, pay_day)
                new_pd = pay_day + relativedelta(months=+i)
                insert_income(user, base_income_amount, new_pd, pay_day_frequency)

        session.commit()
        print(f"Financial App!!\n\nWe are now in the month of {date_today.strftime('%B').upper()}.\n")


# view_all_entries allows you to view all of your bills and income together in order of due date and pay date, totals each, and shows you remaining money at the end of the month.
def view_all_entries():
    from main import Bills, Income, Month 
    from income import insert_income, rr_pay_days 

    vae = engine.execute(f"SELECT bill_name, actual_amount_due, date(due_date) FROM all_entries WHERE date(due_date) between '{this_month.date()}' and '{last_of_month.date()}' ORDER BY DATE(due_date);")
    formatted_result = [f"{bill_name:<20}{actual_amount_due:<14}{due_date:<15}" for bill_name, actual_amount_due, due_date in vae]
    bill_name, actual_amount_due, due_date = "Entry", "Amount", "Date"
    print("\n\nAll entries:\n")
    print('\n'.join([f"{bill_name:<20}{actual_amount_due:<14}{due_date:<15}"] + formatted_result))
    total_income = session.query(func.sum(Income.actual_income_amount)).filter(Income.pay_day.between(this_month.date(),last_of_month.date())).first()[0]
    total_bills = session.query(func.sum(Bills.actual_amount_due)).filter(Bills.due_date.between(this_month.date(),last_of_month.date())).first()[0]
    if total_income and total_bills != None:
        print(f"""
    
The total income for this month is: {total_income}
The total bills for this month is: {total_bills}

You will have this much left over at the end of this month: {total_income - total_bills}""") 
    else:
        pass
    input("\n\nPress ENTER key to continue to main menu.")


