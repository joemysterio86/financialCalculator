# The start of my app.
import os
import time
import datetime
import calendar
import sqlite3
from dateutil import rrule

# defaultPath = os.path.join(os.getcwd(), 'main.db')
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
ddStrf = datetime.datetime.strftime
ddStrp = datetime.datetime.strptime

# rMonth = recurrent.RecurringEvent(now_date=datetime.datetime(2020,1,1))
# rMonth.parse('every first of the month starting january 2020 until january 2050')
# rrMonth = rrule.rrulestr(rMonth.get_RFC_rrule())
# rrMonth.after(dateToday)

# rF = recurrent.RecurringEvent(now_date=datetime.datetime(2020,5,1))
# rF.parse('every other friday starting may st 2020 until january 2040')
# rrF.after(datetime.datetime(2020,4,28))
# cal = calendar.Calendar(firstweekday=6)

# rrF = rrule.rrulestr('DTSTART:20200501\nRRULE:BYDAY=FR;INTERVAL=2;FREQ=WEEKLY;UNTIL=20400101')
# def rFPayDays():
#     for x in rrF:
#         if thisMonth <= x <= rrMonth.after(thisMonth) - datetime.timedelta(days=1):
#             print(x)

# rJ = recurrent.RecurringEvent(now_date=datetime.datetime(2020,5,1))
# rJ.parse('every 1 and 15 of the month starting may 1 2020 until january 2040')
# rJ.parse('DTSTART:20200501\nRRULE:BYMONTHDAY=1,15;INTERVAL=1;FREQ=MONTHLY;UNTIL=20400101')
# rrJ = rrule.rrulestr('DTSTART:20200501\nRRULE:BYMONTHDAY=1,15;INTERVAL=1;FREQ=MONTHLY;UNTIL=20400101')

# def rJPayDays():
#     for x in rrJ:
#         if thisMonth <= x <= lastOfMonth:
#         # if thisMonth <= x <= rrMonth.after(thisMonth) - datetime.timedelta(days=1):
#             print(x)


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

# checkMonth is meant to possibly re-initialize each month to zero if I'm unable to figure best way to get all entries to display for just the current month. last resort...
def checkMonth():
    cur.execute("SELECT * FROM month ORDER BY month DESC LIMIT 1;")
    monthFetch = cur.fetchone()
    if monthFetch == None:
        cur.execute("insert into month (month) values ('2020,1,1');")
        con.commit()
    cur.execute("SELECT * FROM month ORDER BY month DESC LIMIT 1;")
    monthFetch = cur.fetchone()[1]
    if dateToday < rrMonth.after(dateToday):
        if monthFetch == str(thisMonth):
            print(f"Financial App!!\n\nWe are now in the month of {dateToday.strftime('%B').upper()}.\n")
        else:
            print("New month started! Initializing...")
            cur.execute(f"insert into month (month) values(datetime('{dateToday}','start of month'));")
            con.commit()
            time.sleep(1)
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
        print(f"""Financial App!


Today's date is: {dateToday.date()}
""")

# viewAllEntries allows you to view all of your bills and income together in order of due date and pay date, totals each, and shows you remaining money at the end of the month.
def viewAllEntries():
    cur.execute("create temp view if not exists all_entries as select bill_name, actual_amount_due, due_date from bills union select user, income_amount, pay_day_start from income;")
    cur.execute("select bill_name, actual_amount_due, date(due_date) from all_entries order by date(due_date);")
    formatted_result = [f"{bill_name:<20}{actual_amount_due:<14}{due_date:<15}" for bill_name, actual_amount_due, due_date in cur.fetchall()]
    bill_name, actual_amount_due, due_date = "Entry", "Amount", "Date"
    print("\n\nAll entries:\n")
    print('\n'.join([f"{bill_name:<20}{actual_amount_due:<14}{due_date:<15}"] + formatted_result))
    cur.execute("select sum(income_amount) from income;")
    totalIncome = cur.fetchone()[0]
    cur.execute("select sum(actual_amount_due) from bills;")
    totalBills = cur.fetchone()[0]
    print(f"""
    
The total income for this month is: {totalIncome}
The total bills for this month is: {totalBills}

You will have this much left over at the end of this month: {totalIncome - totalBills}""") 
    input("\n\nPress ENTER key to continue to main menu.")

# the rest are self explantory
def viewYourBills():
    cur.execute("SELECT bill_name, base_amount_due, actual_amount_due, date(due_date) FROM bills ORDER BY DATE(due_date);")
    formatted_result = [f"{bill_name:<20}{base_amount_due:<14}{actual_amount_due:<14}{due_date:<15}" for bill_name, base_amount_due, actual_amount_due, due_date in cur.fetchall()]
    bill_name, base_amount_due, actual_amount_due, due_date = "Bill", "Monthly Due", "Current Due", "Due Date"
    print("\n\nYour Bills:\n")
    print('\n'.join([f"{bill_name:<20}{base_amount_due:<14}{actual_amount_due:<14}{due_date:<15}"] + formatted_result))
    input("\n\nPress ENTER key to continue to main menu.")

def viewYourIncome():
    cur.execute("SELECT user, income_amount, DATE(pay_day_start), pay_day_frequency FROM income ORDER BY DATE(pay_day_start);")
    formatted_result = [f"{user:<15}{income_amount:<16}{pay_day_start:<16}{pay_day_frequency:<15}" for user, income_amount, pay_day_start, pay_day_frequency in cur.fetchall()]
    user, income_amount, pay_day_start, pay_day_frequency = "User", "Payday Amount", "Payday Start", "Payday Frequency"
    print("\n\nYour Income:\n")
    print('\n'.join([f"{user:<15}{income_amount:<16}{pay_day_start:<16}{pay_day_frequency:<15}"] + formatted_result))
    input("\n\nPress ENTER key to continue to main menu.")

def addBill():
    def insertBill(con, bill_name, base_amount_due, actual_amount_due, due_date):
        sql = "insert into bills (bill_name, base_amount_due, actual_amount_due, due_date) values (?, ?, ?, ?)"
        cur.execute(sql, (bill_name, base_amount_due, actual_amount_due, due_date))
        con.commit()
        return cur.lastrowid

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
    bill4a = ddStrp(bill4 + " 0:0:0.000000", "%Y-%m-%d %H:%M:%S.%f")
    print("Thanks, creating this bill...")
    time.sleep(.5)
    insertBill(con, bill1, float(bill2), float(bill3), bill4a)
    print("\n\nBill created! Taking you back to main menu.\n")
    time.sleep(1)

def addIncome():
    def insertIncome(con, user, income_amount, pay_day_start, pay_day_frequency):
        sql = "insert into income (user, income_amount, pay_day_start, pay_day_frequency) values (?, ?, ?, ?)"
        cur.execute(sql, (user, income_amount, pay_day_start, pay_day_frequency))
        con.commit()
        return cur.lastrowid
    # This function will take what's generated as "rr", an rrule, for the amount of times there's a pay date, cycles through each date, and insert it in DB as income. Mainly for biweekly schedule.
    def rrPayDays():
        for x in rr:
            if thisMonth <= x <= lastOfMonth:
                insertIncome(con, incBelong, float(incAmount), str(x), incSched)
                # print(incBelong, incAmount, str(x), incSched)
        print("Thanks, adding income to the database...")
        time.sleep(.5)
    
    lam = str(lastOfMonth.date()).replace('-','')
    schedOptions = ["biweekly","bimonthly","monthly"]
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
        incDate = input("Please enter next expected pay date (ex: 2020-01-31) : ")
        if incDate == "":
            continue
        else:
            break
    while True:
        incSched = input("Please indicate if pay schedule is biweekly, bimonthly, or monthly: ")
        if incSched not in schedOptions:
            continue
        else:
            break
    incDateA = ddStrp(incDate + " 0:0:0.000000", "%Y-%m-%d %H:%M:%S.%f")
    incDateB = str(incDateA.date()).replace('-','')

    if incSched.lower() == "biweekly":
        biweekly = f"BYDAY=FR;INTERVAL=2;FREQ=WEEKLY;UNTIL={lam}"
        rr = rrule.rrulestr(f"DTSTART:{incDateB}\nRRULE:{biweekly}")
    elif incSched.lower() == "bimonthly":
        day1 = ddStrf(incDateA, '%-d')
        day2 = ddStrf(ddStrp(input("You selected bimonthly, what is the 2nd expected pay date (ex: 2020-01-31) : ") + " 0:0:0.000000", "%Y-%m-%d %H:%M:%S.%f"), '%-d')
        bimonthly = f"BYMONTHDAY={day1},{day2};INTERVAL=1;FREQ=MONTHLY;UNTIL={lam}"
        rr = rrule.rrulestr(f"DTSTART:{incDateB}\nRRULE:{bimonthly}")
    elif incSched.lower() == "monthly":
        day1 = ddStrf(incDateA, '%-d')
        monthly = f"BYMONTHDAY={day1};INTERVAL=1;FREQ=MONTHLY;UNTIL={lam}"
        rr = rrule.rrulestr(f"DTSTART:{incDateB}\nRRULE:{monthly}")

    rrPayDays()
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
            addBill()
        elif choice == "5":
            addIncome()
        else:
            print("\nPlease select an appropriate option!")
            time.sleep(.5)

menu()

# cur.execute("select ((select sum(income_amount) from income) - (select sum(actual_amount_due) from bills where date(due_date) between '2020-05-01' and '2020-05-15'))")
