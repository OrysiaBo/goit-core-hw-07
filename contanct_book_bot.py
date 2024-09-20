from datetime import datetime, timedelta

# Базовий клас для полів
class Field:
    def __init__(self, value):
        self.value = value

# Клас для імені
class Name(Field):
    pass

# Клас для телефонів
class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)

# Клас для дня народження
class Birthday(Field):
    def __init__(self, value):
        try:
            # Перевірка та конвертація дати в форматі DD.MM.YYYY
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

# Клас для записів
class Record:
    def __init__(self, name, phone=None, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        if phone:
            self.add_phone(phone)
        if birthday:
            self.add_birthday(birthday)

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def days_to_birthday(self):
        if not self.birthday:
            return None
        today = datetime.now().date()
        next_birthday = self.birthday.value.replace(year=today.year)
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
        return (next_birthday - today).days

# Клас для адресної книги
class AddressBook:
    def __init__(self):
        self.records = {}

    def add_record(self, record):
        self.records[record.name.value] = record

    def find(self, name):
        return self.records.get(name)

    def get_upcoming_birthdays(self):
        today = datetime.now().date()
        upcoming_birthdays = []
        for record in self.records.values():
            if record.birthday:
                days = record.days_to_birthday()
                if days is not None and days <= 7:
                    birthday_info = {
                        "name": record.name.value,
                        "birthday": record.birthday.value.strftime("%d.%m.%Y")
                    }
                    upcoming_birthdays.append(birthday_info)
        return upcoming_birthdays
#декоратор оброюки помилок
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Contact not found."
        except ValueError as ve:
            return str(ve)
        except IndexError:
            return "Invalid input, please provide enough arguments."
    return inner
# команди для бота
@input_error
def add_contact(args, book):
    name, phone = args[:2]
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name, phone)
        book.add_record(record)
        message = "Contact added."
    else:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args[:3]
    record = book.find(name)
    if record:
        for idx, phone in enumerate(record.phones):
            if phone.value == old_phone:
                record.phones[idx] = Phone(new_phone)
                return "Phone number updated."
        return "Old phone number not found."
    else:
        raise KeyError

@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if record:
        return f"{name}: {', '.join(phone.value for phone in record.phones)}"
    else:
        raise KeyError

@input_error
def add_birthday(args, book):
    name, birthday = args[:2]
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday added for {name}."
    else:
        raise KeyError

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday is on {record.birthday.value.strftime('%d.%m.%Y')}."
    else:
        return f"No birthday found for {name}."

@input_error
def show_all(book):
    if book.records:
        return '\n'.join([f"{name}: {', '.join(phone.value for phone in record.phones)}" for name, record in book.records.items()])
    else:
        return "No contacts available."

@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if upcoming:
        return '\n'.join([f"{contact['name']}: {contact['birthday']}" for contact in upcoming])
    else:
        return "No upcoming birthdays within the next 7 days."
#основна функція бота
def parse_input(user_input):
    cmd, *args = user_input.strip().split()
    return cmd.lower(), args

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()


