import json
from pathlib import Path


EMPLOYEES_FILE = Path(__file__).resolve().parent / "employees.json"


def _load_employees():
    with open(EMPLOYEES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_employees(employees):
    with open(EMPLOYEES_FILE, "w", encoding="utf-8") as f:
        json.dump(employees, f, indent=4)

def mark_attendance(employee_id, date, status):
    employees = _load_employees()
    for employee in employees:
        if employee["id"] == employee_id:
            if "attendance" not in employee:
                employee["attendance"] = {"days_present": 0, "days_absent": 0}
            if status == "present":
                employee["attendance"]["days_present"] += 1
            elif status == "absent":
                employee["attendance"]["days_absent"] += 1
            
            _save_employees(employees)
            print(f"Attendance for employee {employee_id} on {date} marked as {status}.")
            return True
        
    print(f"Employee with ID {employee_id} not found.")
    return False
    

def get_attendance(employee_id):
    employees = _load_employees()
    for employee in employees:
        if employee["id"] == employee_id:
            return employee.get("attendance", {"days_present": 0, "days_absent": 0})
    print(f"Employee with ID {employee_id} not found.")
    return None


def calculate_attendance_percentage(employee_id):
    employees = _load_employees()
    for employee in employees:
        if employee["id"] == employee_id:
            attendance = employee.get("attendance", {"days_present": 0, "days_absent": 0})
            total_days = attendance["days_present"] + attendance["days_absent"]
            if total_days == 0:
                return 0
            percentage = (attendance["days_present"] / total_days) * 100
            return percentage
    print(f"Employee with ID {employee_id} not found.")
    return None