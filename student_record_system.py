

import json
import os
import re

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "students.json")

FIELD_WIDTHS = {
    "id": 6,
    "name": 20,
    "age": 5,
    "grade": 10,
    "email": 28,
}




def load_data():
    """Load student records from the JSON file. Returns a list of dicts."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except (json.JSONDecodeError, OSError) as e:
        print(f"[Warning] Could not read data file cleanly ({e}). Starting with empty records.")
        return []


def save_data(students):
    """Persist the list of student records to the JSON file."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(students, f, indent=4)
    except OSError as e:
        print(f"[Error] Could not save data: {e}")




def validate_id(student_id, students, exclude_id=None):
    """ID must be a positive integer (as string) and unique."""
    if not student_id.isdigit():
        return False, "ID must contain digits only."
    if int(student_id) <= 0:
        return False, "ID must be a positive number."
    for s in students:
        if s["id"] == student_id and student_id != exclude_id:
            return False, f"ID '{student_id}' already exists."
    return True, ""


def validate_name(name):
    """Name must be non-empty and contain only letters/spaces/hyphens/apostrophes."""
    name = name.strip()
    if not name:
        return False, "Name cannot be empty."
    if not re.match(r"^[A-Za-z .'-]+$", name):
        return False, "Name can only contain letters, spaces, hyphens, and apostrophes."
    return True, ""


def validate_age(age):
    """Age must be an integer between 3 and 100 (reasonable student range)."""
    if not age.isdigit():
        return False, "Age must be a whole number."
    age_val = int(age)
    if age_val < 3 or age_val > 100:
        return False, "Age must be between 3 and 100."
    return True, ""


def validate_grade(grade):
    grade = grade.strip()
    if not grade:
        return False, "Grade/Class cannot be empty."
    if len(grade) > 15:
        return False, "Grade/Class is too long (max 15 characters)."
    return True, ""


def validate_email(email):
    """Email is optional; if provided, must look like a valid email."""
    email = email.strip()
    if email == "":
        return True, "" 
    pattern = r"^[\w.+-]+@[\w-]+\.[\w.-]+$"
    if not re.match(pattern, email):
        return False, "Email format looks invalid (expected e.g. name@example.com)."
    return True, ""


def prompt_validated(prompt_text, validator, *validator_args):
    """Repeatedly prompt the user until input passes the validator function."""
    while True:
        value = input(prompt_text).strip()
        ok, message = validator(value, *validator_args)
        if ok:
            return value
        print(f"  -> Invalid input: {message}")



def find_student(students, student_id):
    for s in students:
        if s["id"] == student_id:
            return s
    return None


def add_student(students):
    print("\n--- Add New Student ---")
    student_id = prompt_validated("Student ID: ", validate_id, students)
    name = prompt_validated("Full Name: ", validate_name)
    age = prompt_validated("Age: ", validate_age)
    grade = prompt_validated("Grade/Class: ", validate_grade)
    email = prompt_validated("Email (optional, press Enter to skip): ", validate_email)

    student = {
        "id": student_id,
        "name": name,
        "age": age,
        "grade": grade,
        "email": email,
    }
    students.append(student)
    save_data(students)
    print(f"Student '{name}' (ID: {student_id}) added successfully.\n")


def view_students(students):
    print("\n--- All Student Records ---")
    if not students:
        print("No records found.\n")
        return
    print_table(students)
    print(f"Total records: {len(students)}\n")


def update_student(students):
    print("\n--- Update Student ---")
    student_id = input("Enter the Student ID to update: ").strip()
    student = find_student(students, student_id)
    if not student:
        print(f"No student found with ID '{student_id}'.\n")
        return

    print("Leave a field blank to keep its current value.")
    print(f"Current Name : {student['name']}")
    new_name = input("New Name: ").strip()
    if new_name:
        ok, msg = validate_name(new_name)
        if ok:
            student["name"] = new_name
        else:
            print(f"  -> Skipped (invalid): {msg}")

    print(f"Current Age  : {student['age']}")
    new_age = input("New Age: ").strip()
    if new_age:
        ok, msg = validate_age(new_age)
        if ok:
            student["age"] = new_age
        else:
            print(f"  -> Skipped (invalid): {msg}")

    print(f"Current Grade: {student['grade']}")
    new_grade = input("New Grade/Class: ").strip()
    if new_grade:
        ok, msg = validate_grade(new_grade)
        if ok:
            student["grade"] = new_grade
        else:
            print(f"  -> Skipped (invalid): {msg}")

    print(f"Current Email: {student['email']}")
    new_email = input("New Email: ").strip()
    if new_email:
        ok, msg = validate_email(new_email)
        if ok:
            student["email"] = new_email
        else:
            print(f"  -> Skipped (invalid): {msg}")

    save_data(students)
    print(f"Student ID '{student_id}' updated successfully.\n")


def delete_student(students):
    print("\n--- Delete Student ---")
    student_id = input("Enter the Student ID to delete: ").strip()
    student = find_student(students, student_id)
    if not student:
        print(f"No student found with ID '{student_id}'.\n")
        return

    confirm = input(f"Are you sure you want to delete '{student['name']}' (ID: {student_id})? [y/N]: ").strip().lower()
    if confirm == "y":
        students.remove(student)
        save_data(students)
        print("Student record deleted.\n")
    else:
        print("Deletion cancelled.\n")


def search_student(students):
    print("\n--- Search Student ---")
    query = input("Enter Student ID or Name (partial match) to search: ").strip().lower()
    if not query:
        print("Search term cannot be empty.\n")
        return
    results = [
        s for s in students
        if query in s["id"].lower() or query in s["name"].lower()
    ]
    if not results:
        print("No matching records found.\n")
        return
    print_table(results)
    print(f"Found {len(results)} matching record(s).\n")




def print_table(students):
    header = (
        f"{'ID':<{FIELD_WIDTHS['id']}} "
        f"{'Name':<{FIELD_WIDTHS['name']}} "
        f"{'Age':<{FIELD_WIDTHS['age']}} "
        f"{'Grade':<{FIELD_WIDTHS['grade']}} "
        f"{'Email':<{FIELD_WIDTHS['email']}}"
    )
    print(header)
    print("-" * len(header))
    for s in students:
        row = (
            f"{s['id']:<{FIELD_WIDTHS['id']}} "
            f"{s['name']:<{FIELD_WIDTHS['name']}} "
            f"{s['age']:<{FIELD_WIDTHS['age']}} "
            f"{s['grade']:<{FIELD_WIDTHS['grade']}} "
            f"{s['email']:<{FIELD_WIDTHS['email']}}"
        )
        print(row)



MENU = """
========= Student Record System =========
1. Add Student
2. View All Students
3. Update Student
4. Delete Student
5. Search Student
6. Exit
===========================================
"""


def main_menu():
    students = load_data()
    while True:
        print(MENU)
        choice = input("Select an option (1-6): ").strip()

        if choice == "1":
            add_student(students)
        elif choice == "2":
            view_students(students)
        elif choice == "3":
            update_student(students)
        elif choice == "4":
            delete_student(students)
        elif choice == "5":
            search_student(students)
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please choose a number between 1 and 6.\n")


if __name__ == "__main__":
    main_menu()
