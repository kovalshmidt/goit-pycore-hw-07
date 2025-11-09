from collections import UserDict
from datetime import datetime, timedelta

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, name):
        super().__init__(name)


class Phone(Field):
    def __init__(self, phone_number):
        if len(phone_number) == 10 and phone_number.isdigit():
            super().__init__(phone_number)
        else:
            raise ValueError(f"Wrong phone number '{phone_number}' format")
        
    def __str__(self):
        return super().__str__()
        
class Birthday(Field):
    def __init__(self, birthday_date):
        try:
            datetime.strptime(birthday_date, "%d.%m.%Y")
            super().__init__(birthday_date)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))
   
    def add_birthday(self, birthday_date):
        birthday = Birthday(birthday_date)
        self.birthday = birthday

    def remove_phone(self, phone_number):
        phone = self.find_phone(phone_number)
        if phone:
            self.phones.remove(phone)

    def edit_phone(self, old_phone, new_phone):
        phone = self.find_phone(old_phone)
        if phone:
            index = self.phones.index(phone)
            self.phones[index] = Phone(new_phone)

    def find_phone(self, phone_number) -> Phone:
        for phone in self.phones:
            if phone_number == phone.value:
                return phone
        return None

    def delete_phone(self, phone_number):
        phone = self.find_phone(phone_number)
        if phone:
            self.phones.remove(phone)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

class AddressBook(UserDict):

    def add_record(self, record):
        key = record.name.value
        if key not in self.data:
            self.data[key] = record

    def find(self, name) -> 'Record':
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            self.data.pop(name)
    
    def get_upcoming_birthdays(self)-> list:
        upcoming_birthdays = []
        today = datetime.today().date()
        end_date = today + timedelta(days=7)

        for record in self.data.values():
            # Get user birthdat or skip if error
            try:
                birthday_date = datetime.strptime(str(record.birthday), "%d.%m.%Y").date()
            except ValueError:
                print(f"Error in date format for {record.name}: {record.birthday}")
                continue

            # Transform in this year date
            birthday_this_year = birthday_date.replace(year=today.year)

            # Set next year for a passed birthday
            if birthday_this_year < today:
                birthday_this_year = birthday_date.replace(year=today.year + 1)

            # Check if the birthday is in the upcoming 7 days
            if today <= birthday_this_year < end_date:
                congratulation_date = birthday_this_year
                day_of_week = birthday_this_year.weekday()

                if day_of_week == 5:
                    congratulation_date = birthday_this_year + timedelta(days=2)
                elif day_of_week == 6:
                    congratulation_date = birthday_this_year + timedelta(days=1)

                upcoming_birthdays.append({
                    "name": record.name, "congratulation_date": congratulation_date.strftime("%d.%m.%Y")
                })

        return upcoming_birthdays

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (IndexError, KeyError):
            return "Enter the argument for the command"
        except ValueError as e:
            return str(e)

    return inner

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book: AddressBook):
    name, phone_number, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone_number:
        record.add_phone(phone_number)

    return message

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Contact updated."
    else:
        return f"No contact found with name: {name}"

@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record:
        return f"{name}: {', '.join(str(p) for p in record.phones)}"
    else:
        return f"No contact found with name: {name}"
    
def show_all(book: AddressBook):
    if not book.data:
        return "No contacts found."
    result = []
    for record in book.data.values():
        result.append(f"{record.name}: {', '.join(str(p) for p in record.phones)}")
    return "\n".join(result)

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday_date = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday_date)
        return "Birthday added."
    else:
        return f"No contact found with name: {name}"


@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record:
        return f"{name}: {record.birthday}"
    else:
        return f"No contact found with name: {name}"
    

@input_error
def birthdays(book: AddressBook):
    birthdays_list = book.get_upcoming_birthdays()
    if birthdays_list:
        lines = [
            f"{b['name']}: {b['congratulation_date']}" for b in birthdays_list
        ]
        return "\n".join(lines)
    else:
        return "There are no upcoming birthdays"



def main():
    contacts = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ").strip()
        if not user_input:
            continue

        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, contacts))
        elif command == "change":
            print(change_contact(args, contacts))
        elif command == "phone":
            print(show_phone(args, contacts))
        elif command == "all":
            print(show_all(contacts))
        elif command == "add-birthday":
            print(add_birthday(args, contacts))
        elif command == "show-birthday":
            print(show_birthday(args, contacts))
        elif command == "birthdays":
            print(birthdays(contacts))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()

# hello # How can I help you?
# add ihor 123 # Wrong phone number '123' format
# add ihor 1234567890 # Contact updated.
# add alex 0987654321 # Contact added.
# phone alex # alex: 0987654321
# change alex 0987654321 0000000000 # Contact updated.
# phone alex # alex: 0000000000
# add alex 1111111111 # Contact updated.
# all 
    # ihor: 1234567890
    # alex: 0987654321, 1111111111
# add-birthday 27.08.1991 # not enough values to unpack (expected 2, got 1)
# add-birthday ihor 1991.08.27  # Invalid date format. Use DD.MM.YYYY
# add-birthday ihor 27.08.1991 # Birthday added.
# show-birthday ihor # ihor: 27.08.1991
# add-birthday alex 28.08.1991 # Birthday added.
# birthdays # There are no upcoming birthdays
# add marta 7771113330 # Contact added.
# add-birthday marta 13.11.1991 # Birthday added.
# birthdays # marta: 13.11.2025
