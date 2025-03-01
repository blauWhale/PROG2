'''

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
    
'''

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