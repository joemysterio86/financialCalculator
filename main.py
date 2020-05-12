#!/usr/bin/env python3
import os
import time
import datetime
import calendar
import sqlite3
from dateutil import rrule
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

# this is the default path for the database, function is to create the connection to DB and a cursor
defaultPath = os.path.join(os.path.dirname(__file__), 'main.db')
def dbConnect(dbPath=defaultPath):
    con = sqlite3.connect(dbPath)
    return con
con = dbConnect()
cur = con.cursor()

# self explanatory
dateToday = datetime.datetime.today()
thisMonth = dateToday.replace(day=1,hour=0,minute=0,second=0,microsecond=0)
rrMonth = rrule.rrulestr('DTSTART:20200101\nRRULE:BYMONTHDAY=1;INTERVAL=1;FREQ=MONTHLY;UNTIL=20500101')
lastOfMonth = rrMonth.after(thisMonth) - datetime.timedelta(days=1)

billsTableCreate = """
CREATE TABLE IF NOT EXISTS bills (
    id integer PRIMARY KEY,
    bill_name varchar(255) NOT NULL,
    base_amount_due real NOT NULL,
    actual_amount_due real NOT NULL,
    due_date datetime NOT NULL
);"""

incomeTableCreate = """
CREATE TABLE IF NOT EXISTS income (
	id integer PRIMARY KEY,
	user varchar(255) NOT NULL,
	income_amount real NOT NULL,
	pay_day_start datetime NOT NULL,
	pay_day_frequency varchar(255) NOT NULL
);"""

monthTableCreate = """
CREATE TABLE IF NOT EXISTS month (
    id integer PRIMARY KEY,
    month datetime NOT NULL
);"""

cur.execute(billsTableCreate)
cur.execute(incomeTableCreate)
cur.execute(monthTableCreate)

# checkMonth is meant to re-initialize each month to zero if it's a new month.
def checkMonth():
    # gets the difference in months to be used in relativedelta.
    def diff_month(d1, d2):
        return (d1.year - d2.year) * 12 + d1.month - d2.month
    
    # checks if month table is empty, if so, adds a base month.
    cur.execute("SELECT * FROM month ORDER BY month DESC LIMIT 1;")
    monthFetch = cur.fetchone()
    if monthFetch == None:
        cur.execute("insert into month (month) values ('2000,1,1');")
        con.commit()

    # checks the current month, if not, sets up a new month to be current, resets bills back to original amount due, and updates income to new/current month.
    cur.execute("SELECT * FROM month ORDER BY month DESC LIMIT 1;")
    monthFetch = cur.fetchone()[1]
    if monthFetch == str(thisMonth):
        print(f"Financial App!!\n\nWe are now in the month of {dateToday.strftime('%B').upper()}.\n")
    else:
        print("New month started! Initializing...\n\n\n")
        cur.execute(f"insert into month (month) values(datetime('{dateToday}','start of month'));")
        
        # loops through all entries and sets the actual amount due back to the base amount, and increases the due date to the current month.
        cur.execute("select id, due_date from bills;")
        for id, due_date in cur.fetchall():
            i = diff_month(dateToday, parse(due_date))
            newDate = parse(due_date) + relativedelta(months=+i)
            cur.execute(f"update bills set due_date = datetime('{newDate}'), actual_amount_due = base_amount_due where id = {id}")
        
        # loops through income table and updates/increases the pay day to the current month.
        cur.execute("""SELECT id, user, pay_day_frequency, pay_day_start, income_amount FROM income WHERE pay_day_frequency = 'weekly' OR pay_day_frequency = 'biweekly' GROUP BY user
UNION ALL
SELECT id, user, pay_day_frequency, pay_day_start, income_amount FROM income WHERE pay_day_frequency = 'bimonthly' OR pay_day_frequency = 'monthly';""")
        for id, user, pay_day_frequency, pay_day_start, income_amount in cur.fetchall():
            if pay_day_frequency == 'weekly':
                pds = parse(pay_day_start)
                rruleDate = str(pds.date()).replace('-','')
                rrPayDays(pay_day_frequency, rruleDate, user, income_amount, pds)
            elif pay_day_frequency == 'biweekly':
                pds = parse(pay_day_start)
                rruleDate = str(pds.date()).replace('-','')
                rrPayDays(pay_day_frequency, rruleDate, user, income_amount, pds)
            else:
                i = diff_month(dateToday, parse(pay_day_start))
                pds = parse(pay_day_start) + relativedelta(months=+i)
                insertIncome(con, user, income_amount, pds, pay_day_frequency)
        con.commit()
        print(f"Financial App!!\n\nWe are now in the month of {dateToday.strftime('%B').upper()}.\n")

# nextBill is to show you today's date along with what is and how much your next bill will be.
def nextBill():
    # cur.execute("select bill_name, base_amount_due from bills where date(due_date) = (select min(date(due_date)) from bills where date(due_date) > date(\"2020-05-02\"));")
    cur.execute("select bill_name, base_amount_due from bills where date(due_date) = (select min(date(due_date)) from bills where date(due_date) >= date(\"now\"));")
    bill = cur.fetchone()
    if bill:
        print(f"""Today's date is: {dateToday.date()}
Your next bill is {bill[0].upper()} for the amount of {bill[1]}.
""")
    else:
        print(f"Today's date is: {dateToday.date()}")

# viewAllEntries allows you to view all of your bills and income together in order of due date and pay date, totals each, and shows you remaining money at the end of the month.
def viewAllEntries():
    cur.execute("CREATE TEMP VIEW IF NOT EXISTS all_entries as SELECT bill_name, actual_amount_due, due_date FROM bills union SELECT user, income_amount, pay_day_start FROM income;")
    cur.execute(f"SELECT bill_name, actual_amount_due, date(due_date) FROM all_entries WHERE date(due_date) between '{thisMonth.date()}' and '{lastOfMonth.date()}' ORDER BY DATE(due_date);")
    formatted_result = [f"{bill_name:<20}{actual_amount_due:<14}{due_date:<15}" for bill_name, actual_amount_due, due_date in cur.fetchall()]
    bill_name, actual_amount_due, due_date = "Entry", "Amount", "Date"
    print("\n\nAll entries:\n")
    print('\n'.join([f"{bill_name:<20}{actual_amount_due:<14}{due_date:<15}"] + formatted_result))
    cur.execute(f"SELECT sum(income_amount), pay_day_start FROM income WHERE date(pay_day_start) between '{thisMonth.date()}' and '{lastOfMonth.date()}';")
    totalIncome = cur.fetchone()[0]
    cur.execute("SELECT sum(actual_amount_due) FROM bills;")
    totalBills = cur.fetchone()[0]
    if totalIncome and totalBills != None:
        print(f"""
    
The total income for this month is: {totalIncome}
The total bills for this month is: {totalBills}

You will have this much left over at the end of this month: {totalIncome - totalBills}""") 
    else:
        pass
    input("\n\nPress ENTER key to continue to main menu.")

# the next four are self explantory
def viewYourBills():
    cur.execute("SELECT bill_name, base_amount_due, actual_amount_due, date(due_date) FROM bills ORDER BY DATE(due_date);")
    formatted_result = [f"{bill_name:<20}{base_amount_due:<14}{actual_amount_due:<14}{due_date:<15}" for bill_name, base_amount_due, actual_amount_due, due_date in cur.fetchall()]
    bill_name, base_amount_due, actual_amount_due, due_date = "Bill", "Monthly Due", "Current Due", "Due Date"
    print("\n\nYour Bills:\n")
    print('\n'.join([f"{bill_name:<20}{base_amount_due:<14}{actual_amount_due:<14}{due_date:<15}"] + formatted_result))
    input("\n\nPress ENTER key to continue to main menu.")

def viewYourIncome():
    cur.execute(f"SELECT user, income_amount, DATE(pay_day_start), pay_day_frequency FROM income WHERE date(pay_day_start) between '{thisMonth.date()}' and '{lastOfMonth.date()}' ORDER BY DATE(pay_day_start);")
    formatted_result = [f"{user:<15}{income_amount:<16}{pay_day_start:<16}{pay_day_frequency:<15}" for user, income_amount, pay_day_start, pay_day_frequency in cur.fetchall()]
    user, income_amount, pay_day_start, pay_day_frequency = "User", "Payday Amount", "Payday Start", "Payday Frequency"
    print("\n\nYour Income:\n")
    print('\n'.join([f"{user:<15}{income_amount:<16}{pay_day_start:<16}{pay_day_frequency:<15}"] + formatted_result))
    input("\n\nPress ENTER key to continue to main menu.")

def insertBill(con, bill_name, base_amount_due, actual_amount_due, due_date):
    sql = "insert into bills (bill_name, base_amount_due, actual_amount_due, due_date) values (?, ?, ?, ?)"
    cur.execute(sql, (bill_name, base_amount_due, actual_amount_due, due_date))
    con.commit()
    return cur.lastrowid

def insertIncome(con, user, income_amount, pay_day_start, pay_day_frequency):
    sql = "insert into income (user, income_amount, pay_day_start, pay_day_frequency) values (?, ?, ?, ?)"
    cur.execute(sql, (user, income_amount, pay_day_start, pay_day_frequency))
    con.commit()
    return cur.lastrowid

# This function will take what's generated as "rr", an rrulestr, for the amount of times there's a pay date, cycles through each date, and insert it in DB as income. Mainly for biweekly schedule.
def rrPayDays(*args):
    lam = str(lastOfMonth.date()).replace('-','')
    if args[0].lower() == "weekly":
        biweekly = f"BYDAY=FR;INTERVAL=1;FREQ=WEEKLY;UNTIL={lam}"
        rr = rrule.rrulestr(f"DTSTART:{args[1]}\nRRULE:{biweekly}")
    elif args[0].lower() == "biweekly":
        biweekly = f"BYDAY=FR;INTERVAL=2;FREQ=WEEKLY;UNTIL={lam}"
        rr = rrule.rrulestr(f"DTSTART:{args[1]}\nRRULE:{biweekly}")
    for x in rr:
        if thisMonth <= x <= lastOfMonth:
            insertIncome(con, args[2], float(args[3]), str(x), args[0])
            # print(args[2], float(args[3]), str(x), args[0])

def billQ():
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
        bill4 = input("Please enter the bill due date (YYYY-MM-DD): ")
        if bill4 == "":
            continue
        else:
            break
    bill4a = parse(bill4)
    print("Thanks, creating this bill...")
    time.sleep(.5)
    insertBill(con, bill1, float(bill2), float(bill3), bill4a)
    print("\n\nBill created! Taking you back to main menu.\n")
    time.sleep(1)

def incomeQ():
    schedOptions = ["weekly","biweekly","bimonthly","monthly"]
    while True:
        incBelong = input("\nPlease enter who this income belongs to: ")
        if incBelong == "":
            continue
        else:
            break
    while True:
        incAmount = input("Please enter paycheck amount: ")
        if incAmount == "":
            continue
        else:
            break
    while True:
        incDate1 = input("Please enter next expected pay date (ex: 2020-01-31) : ")
        if incDate1 == "":
            continue
        else:
            break
    while True:
        incSched = input("Please indicate if pay schedule is weekly, biweekly, bimonthly, or monthly: ")
        if incSched not in schedOptions:
            continue
        else:
            break

    incDate1A = parse(incDate1)
    rruleDate = str(incDate1A.date()).replace('-','')
    if incSched == "bimonthly":
        incDate2 = input("You selected bimonthly, what is the 2nd expected pay date (ex: 2020-01-31) : ")
        incDate2A = parse(incDate2)
        print("Thanks, adding income to the database...")
        insertIncome(con, incBelong, incAmount, incDate1A, incSched)
        insertIncome(con, incBelong, incAmount, incDate2A, incSched)
    elif incSched == "monthly":
        print("Thanks, adding income to the database...")
        insertIncome(con, incBelong, incAmount, incDate1A, incSched)
    else:
        rrPayDays(incSched, rruleDate, incBelong, incAmount, incDate1A)
    
    print("\n\nIncome added for entire month! Taking you back to main menu.\n")
    time.sleep(1)
        
def menu():
    while True:
        checkMonth()
        nextBill()
        print(f"""What would you like to do?

        1) View all entries.
        2) View your bills only.
        3) View your income only.
        4) Add a bill.
        5) Add income.
        Q) Exit.

        """)
        choice = input("Please select an option: ")
        if choice.lower() == "q":
            print("You selected Q, exiting...")
            exit()
        elif choice == "1":
            viewAllEntries()
        elif choice == "2":
            viewYourBills()
        elif choice == "3":
            viewYourIncome()
        elif choice == "4":
            billQ()
        elif choice == "5":
            incomeQ()
        else:
            print("\nPlease select an appropriate option!")
            time.sleep(.5)

menu()
