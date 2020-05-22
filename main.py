import time
from other import check_month, view_all_entries
from bills import bills_questions, next_bill
from bank import bank_questions
from income import income_questions

def menu():
    while True:
        check_month()
        next_bill()
        print(f"""What would you like to do?

    1) View all entries.
    2) Bank (View/Add/Update/Delete)
    3) Income (View/Add/Update/Delete)
    4) Bills (View/Add/Update/Delete)
    Q) Exit.

    """)
        choice = input("Please select an option: ")
        if choice.lower() == "q":
            print("You selected Q, exiting...")
            exit()
        elif choice == "1":
            view_all_entries()
        elif choice == "2":
            bank_questions()
        elif choice == "3":
            income_questions()
        elif choice == "4":
            bills_questions()
        else:
            print("\nPlease select an appropriate option!")
            time.sleep(.5)

menu()
