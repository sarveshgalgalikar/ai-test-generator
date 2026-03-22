# Variables hold data
feature_name = "Login Form"
num_tests = 5

# f-strings let you embed variables inside text
prompt = f"Generate {num_tests} test cases for the {feature_name}"
print(prompt)

# Functions = reusable blocks of code
def build_prompt(feature, num_cases):
    return f"Generate {num_cases} test cases for: {feature}"

# Now call it with different inputs
prompt1 = build_prompt("Login Form", 5)
prompt2 = build_prompt("Shopping Cart", 3)
print(prompt1)
print(prompt2)

# Dictionaries = key-value pairs (like JSON)
test_case = {
    "id": 1,
    "title": "Empty password field",
    "priority": "high",
    "steps": ["Navigate to login", "Enter username", "Leave password empty", "Click submit"]
}

# Access values by key
print(test_case["title"])
print(test_case["priority"])

# Loop through the steps
for step in test_case["steps"]:
    print(f"  - {step}")


# Without error handling, one failure crashes everything
# With it, you stay in control

def safe_divide(a, b):
    try:
        result = a / b
        return result
    except ZeroDivisionError:
        print("Can't divide by zero!")
        return None

print(safe_divide(10, 2))
print(safe_divide(10, 0))