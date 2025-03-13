# 1. Bank Account Implementation

This is a simple implementation of a `BankAccount` class in Python that provides basic banking functionality including deposits, withdrawals, balance checks, and account closure. The implementation enforces constraints such as maximum balance limits and prevents operations on closed accounts.

[Link to bankAccount.py](./bankAccount.py)

## Code

```python
class BankAccount:

    """
    A class representing a simple bank account with basic operations.
    
    This class implements standard bank account functionalities including deposits,
    withdrawals, balance checks, and account closure. It also enforces constraints
    such as maximum balance limit and prevents operations on closed accounts.
    """
    def __init__(self, identifier):
        """
        New accounts start with a zero balance
        Accounts are open by default when created
        """
        self.identifier = identifier
        self.balance = 0
        self.is_open = True

    def deposit(self, amount):
        """
        Parameters:
            amount (float): The amount to deposit
            
        Checks:
            - Account must be open
            - Amount must be positive
            - Total balance must not exceed 100K
        """
        if self.is_open and amount > 0 and self.balance + amount <= 100000:
            self.balance += amount
        else:
            print("Invalid deposit.")

    def withdraw(self, amount):

        """
        Parameters:
            amount (float): The amount to withdraw
            
        Checks:
            - Account must be open
            - Amount must be positive
            - Balance must be sufficient for withdrawal
        """
        if self.is_open and amount > 0 and self.balance - amount >= 0:
            self.balance -= amount
        else:
            print("Invalid withdrawal.")

    def get_balance(self):
        return self.balance

    def close_account(self):

        """
        Checks:
            - Account balance must be zero
        """
        if self.balance == 0:
            self.is_open = False
        else:
            print("Invalid close.")

if __name__ == "__main__":
    account = BankAccount("IBAN12345678")
    
    print("Depositing 5000...")
    account.deposit(5000)
    print("Balance:", account.get_balance())
    
    print("Withdrawing 1500...")
    account.withdraw(1500)
    print("Balance:", account.get_balance())
    
    print("Trying to close account...")
    account.close_account()

    print("Withdrawing the rest amount... 3500.")
    account.withdraw(3500)
    print("Balance:", account.get_balance())

    print("Trying to close account again... account is closed now.")
    account.close_account()

    print("Trying to deposit after closing...")
    account.deposit(1000)
```

# 2. Classroom Model Implementation

This implementation models a classroom environment with teachers, students, documents, tables, and a blackboard. The program creates a teacher with 20 documents, distributes these documents to 20 students, organizes students into tables, and displays the teacher's name on the blackboard.

[Link to P01_part2.py](./P01_part2.py)

## Code

```python

"""

Classes:
    teacher
    student
    document
    table
    blackboard
    
Instanciate objects:
    1 teacher with 20 objects
    each student gets 1 document from teacher
    blackboard displays teachers name
    
"""

class Teacher:
    """Represents a teacher who has a certain number of documents"""
    def __init__(self, name, num_documents):
        self.name = name
        self.documents = [Document() for _ in range(num_documents)]  # Create 20 documents


class Student:
    """Represents a student with a document"""
    def __init__(self, name, document):
        self.name = name
        self.document = document  # Each student owns one document


class Document:
    """Represents a document given to students"""
    def __init__(self):
        self.owner = None  # Owner (Student) will be assigned later


class Table:
    """Represents a table occupied by two students"""
    def __init__(self, student1, student2):
        self.students = [student1, student2]  # A table has two students


class Blackboard:
    """Represents a blackboard displaying the teacher's name"""
    def __init__(self, teacher):
        self.message = f"Teacher: {teacher.name}"  # Blackboard shows teacher's name


# Step 1: Instantiate a Teacher with 20 documents
teacher = Teacher("Mr. Smith", 20)

# Step 2: Create 20 students and assign each one a document
students = []
for i in range(20):
    student = Student(f"Student {i+1}", teacher.documents[i])
    teacher.documents[i].owner = student  # Assign document to student
    students.append(student)

# Step 3: Create 10 tables, each occupied by 2 students
tables = []
for i in range(0, 20, 2):  # Step by 2 to get pairs of students
    table = Table(students[i], students[i+1])
    tables.append(table)

# Step 4: Create a blackboard displaying the teacher's name
blackboard = Blackboard(teacher)

# Step 5: Print the classroom setup
print("\nClassroom Setup:")
print(f"Teacher: {teacher.name}")
print(f"Blackboard Message: {blackboard.message}\n")

for index, table in enumerate(tables, start=1):
    print(f"Table {index}: {table.students[0].name} and {table.students[1].name}")

print("\nEach student has a document:")
for student in students:
    print(f"{student.name} owns a document.")
```