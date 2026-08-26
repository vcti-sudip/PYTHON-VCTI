def calculate_salary(employee):
    return employee.get("salary", 0)

def calculate_bonus(employee):
    return employee.get("bonus", 0)

def calculate_deductions(employee):
    return employee.get("deductions", 0)

def calculate_net_salary(employee):
    salary = calculate_salary(employee)
    bonus = calculate_bonus(employee)
    deductions = calculate_deductions(employee)
    net_salary = salary + bonus - deductions
    return net_salary
