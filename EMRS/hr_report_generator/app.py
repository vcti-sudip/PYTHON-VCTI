from employee_system.employee import get_all_employees

import jinja2
from prettytable import PrettyTable
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"


def render_employee_report(employee):
	env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATES_DIR))
	template = env.get_template("employee_report.txt")
	return template.render(employee=employee)


def print_employee_table(employees):
	table = PrettyTable()
	table.field_names = ["ID", "Name", "Department", "Salary"]

	for employee in employees:
		table.add_row(
			[
				employee.get("id", ""),
				employee.get("name", ""),
				employee.get("department", ""),
				employee.get("salary", 0),
			]
		)

	print("Employee Table")
	print("==============")
	print(table)


def main():
	employees = get_all_employees()

	print("=" * 40)
	print(" HR EMPLOYEE REPORT")
	print("=" * 40)

	for employee in employees:
		report = render_employee_report(employee)
		print(report.rstrip())
		print()

	print_employee_table(employees)


if __name__ == "__main__":
	main()
