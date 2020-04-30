# The start of my app.
import os, time, datetime, calendar, sqlite3
from dateutil import rrule
import recurrent

dateToday = datetime.datetime.today()
# r = recurrent.RecurringEvent(now_date=dateToday)
# r = recurrent.RecurringEvent(now_date=datetime.datetime(2020,1,1))
# r.parse('every other friday starting now until january 2050')
# rr = rrule.rrulestr(r.get_RFC_rrule())
# rr.after(datetime.datetime(2020,4,38)
# cal = calendar.Calendar(firstweekday=6)


defaultPath = os.path.join(os.path.dirname(__file__), 'finanCalc.db')
def dbConnect(dbPath=defaultPath):
    con = sqlite3.connect(dbPath)
    return con

con = dbConnect()
cur = con.cursor()

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

cur.execute(billsTableCreate)
cur.execute(incomeTableCreate)

def addBill():
    def insertBill(con, bill_name, base_amount_due, actual_amount_due, due_date):
        sql = "insert into bills (bill_name, base_amount_due, actual_amount_due, due_date) values (?, ?, ?, ?)"
        cur.execute(sql, (bill_name, base_amount_due, actual_amount_due, due_date))
        con.commit()
        return cur.lastrowid

    bill1 = input("\nPlease enter the bill name: ")
    bill2 = float(input("Please enter what is normally due: "))
    bill3 = float(input("Please enter what you will pay: "))
    bill4a = input("Please enter the bill due date (YYYY-MM-DD): ")
    bill4b = datetime.datetime.strptime(bill4a + " 0:0:0.000000", "%Y-%m-%d %H:%M:%S.%f")
    time.sleep(.5)
    print("Thanks, creating this bill...")
    insertBill(con, bill1, bill2, bill3, bill4b)
    print("Bill created!! Taking you back to main menu.")
    time.sleep(1.5)

def addIncome():
    def insertIncome(con, user, income_amount, pay_day_start, pay_day_frequency):
        sql = "insert into income (user, income_amount, pay_day_start, pay_day_frequency) values (?, ?, ?, ?)"
        cur.execute(sql, (user, income_amount, pay_day_start, pay_day_frequency))
        con.commit()
        return cur.lastrowid

    income1 = input("\nPlease enter who this income belongs to: ")
    income2 = float(input("Please enter paycheck amount: "))
    income3a = input("Please enter next expected pay date (ex: 2020-01-01) : ")
    income3b = datetime.datetime.strptime(income3a + " 0:0:0.000000", "%Y-%m-%d %H:%M:%S.%f")
    income4 = input("Please indicate if pay schedule is biweekly, bimonthly, or monthly: ")
    time.sleep(.5)
    print("Thanks, adding income to the database...")
    insertIncome(con, income1, income2, income3b, income4)
    print("Income added!! Taking you back to main menu.")
    time.sleep(1.5)

def nextBill():
    # cur.execute("select bill_name, base_amount_due from bills where date(due_date) = (select min(date(due_date)) from bills where date(due_date) > date(\"2020-05-02\"));")
    cur.execute("select bill_name, base_amount_due from bills where date(due_date) = (select min(date(due_date)) from bills where date(due_date) > date(\"now\"));")
    bill = cur.fetchone()
    if bill != None:
        print(f"""Financial App!


Today's date is: {dateToday.date()}
Your next bill is {bill[0].upper()} for the amount of {bill[1]}.
""")
    else:
        print(f"""Financial App!


Today's date is: {dateToday.date()}
""")
        
def viewAllEntries():
    cur.execute("create table all_entries as select bill_name, actual_amount_due, due_date from bills union select user, income_amount, pay_day_start from income;")
    con.commit()
    cur.execute("select bill_name, actual_amount_due, date(due_date) from all_entries order by date(due_date);")
    formatted_result = [f"{bill_name:<20}{actual_amount_due:<14}{due_date:<15}" for bill_name, actual_amount_due, due_date in cur.fetchall()]
    bill_name, actual_amount_due, due_date = "Entry", "Amount", "Date"
    print("\n\nAll entries:\n")
    print('\n'.join([f"{bill_name:<20}{actual_amount_due:<14}{due_date:<15}"] + formatted_result))
    input("\n\nPress ENTER key to continue to main menu.")
    cur.execute("drop table all_entries;")
    con.commit()

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
    print("\n\nYour Bills:\n")
    print('\n'.join([f"{user:<15}{income_amount:<16}{pay_day_start:<16}{pay_day_frequency:<15}"] + formatted_result))
    input("\n\nPress ENTER key to continue to main menu.")


def menu():
    nextBill()
    print(f"""What would you like to do?

    1) View all entries.
    2) View your bills only.
    3) View your income only.
    4) Add a bill.
    5) Add income.
    Q) Exit.

    Please press a number 1-4 to choose.

    """)
    choice = input("Please select an option: ")
    if choice.lower() == "q":
        print("You selected Q, exiting...")
        exit()
    elif choice == "1":
        viewAllEntries()
        menu()
    elif choice == "2":
        viewYourBills()
        menu()
    elif choice == "3":
        viewYourIncome()
        menu()
    elif choice == "4":
        addBill()
        menu()
    elif choice == "5":
        addIncome()
        menu()
    else:
        print("PLEASE!!! Select an appropriate option!")
        time.sleep(1)
        menu()


menu()
