import json
from pathlib import Path

EMPLOYEES_FILE = Path(__file__).resolve().parent / "employees.json"


def _load_employees():
    with open(EMPLOYEES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_employees(employees):
    with open(EMPLOYEES_FILE, "w", encoding="utf-8") as f:
        json.dump(employees, f, indent=4)


def add_employee(employee):
    employees = _load_employees()
    employees.append(employee)
    _save_employees(employees)
    
        
def get_employee(employee_id):
    employees = _load_employees()
    for employee in employees:
        if employee["id"] == employee_id:
            return employee
    return None


def get_all_employees():
    return _load_employees()