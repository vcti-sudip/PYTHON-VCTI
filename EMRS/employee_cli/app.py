from tabulate import tabulate
from rich.console import Console
from rich.table import Table

from employee_system.employee import get_all_employees, get_employee

BANNER_WIDTH = 40

def show_tabulate_table(employees, table_format):
    print(tabulate(employees, headers="keys", tablefmt=table_format))
    
    
def show_rich_table(employees):
    console = Console()
    table = Table(title = "Employee Details")
    
    table.add_column("ID", justify="left")
    table.add_column("Name", justify="left")
    table.add_column("Department", justify="left")
    table.add_column("Salary", justify="right")
    
    for employee in employees:
        table.add_row(str(employee["id"]), employee["name"], employee["department"], str(employee["salary"]))
    console.print(table)
    

def main():
    employees = get_all_employees()
    
    print("=" * BANNER_WIDTH)
    print("Employee Management System".center(BANNER_WIDTH))
    print("=" * BANNER_WIDTH)
    print()
    
    print("Employee List: - Tabulate (grid)")
    print("-" * BANNER_WIDTH)
    show_tabulate_table(employees, "grid")
    print()
    
    print("Employee List: - Tabulate (simple)")
    print("-" * BANNER_WIDTH)
    show_tabulate_table(employees, "simple")
    print()
    
    print("Employee List: - Rich")
    print("-" * BANNER_WIDTH)
    show_rich_table(employees)
    
    
if __name__ == "__main__":
    main()