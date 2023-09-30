import json
import sys
import os
from dotenv import load_dotenv
from inventree.api import InvenTreeAPI
from inventree.part import Part
from inventree.stock import StockItem

# Parse command line arguments
user_category = sys.argv[1] if len(sys.argv) >= 2 else ""
num_ipns_to_generate = int(sys.argv[2]) if len(sys.argv) >= 3 else 0
num_packaging_needed = int(sys.argv[3]) if len(sys.argv) >= 4 else 0

# Load environment variables from .env file
load_dotenv()

# Specify the path to the file containing URLs
path = "input.json"

# Clear the contents of the input file
with open(path, "w"):
    pass

# Create an instance of the Inventree API
SERVER_ADDRESS = os.environ.get('INVENTREE_SERVER_ADDRESS')
MY_USERNAME = os.environ.get('INVENTREE_USERNAME')
MY_PASSWORD = os.environ.get('INVENTREE_PASSWORD')
api = InvenTreeAPI(SERVER_ADDRESS, username=MY_USERNAME,
                   password=MY_PASSWORD, timeout=3600)

try:
    # Request the list of parts through the API
    parts = Part.list(api)

    # Order the list of parts by IPN
    parts.sort(key=lambda x: str(x.IPN))

    # Prepare a list of dictionaries for parts data
    parts_data = [{"name": part.name, "IPN": part.IPN,
                   "ID": part.pk, "packaging": ""} for part in parts]

    # Retrieve all stock items through the API
    stock_items = StockItem.list(api)

    # Update the JSON with the "packaging" field from the StockItems API
    for item in parts_data:
        part_ipn = item['IPN']
        part_obj = next((part for part in parts if part.IPN == part_ipn), None)

        if part_obj:
            stock_items_for_part = [
                stock_item for stock_item in stock_items if stock_item.part == part_obj.pk]

            if stock_items_for_part:
                stock_item = stock_items_for_part[0]
                item['packaging'] = stock_item.packaging

    # Write the list of parts_data to the input file in JSON format
    with open(path, 'w') as f:
        json.dump(parts_data, f)

except Exception as e:
    print("An error occurred:", str(e))

# Load data from the JSON file
with open(path) as f:
    data = json.load(f)

# Dictionary to track IPNs used in each category
used_ipns = {}

# Loop through all elements in the JSON file
for item in data:
    ipn_code = item['IPN'].strip()
    ipn_code = str(ipn_code).rjust(12, '0')
    category = ipn_code[:6].replace(' ', '0')

    if category in used_ipns:
        used_ipns[category].add(ipn_code)
    else:
        used_ipns[category] = {ipn_code}

# Calculate the maximum value of the last 6 digits of IPNs for each category
max_last_6_digits = {category: max(
    int(ipn[-6:]) for ipn in ipns) for category, ipns in used_ipns.items()}

# Prompt user for category if not provided through terminal arguments
if not user_category:
    user_category = input(
        "Enter the category for which you want to generate the next IPN: ")

# Check if the category exists in the "used_ipns" dictionary
if user_category in used_ipns:
    ipns_list = sorted(list(used_ipns[user_category]))
    if len(ipns_list) == 0:
        max_last_6_digits[user_category] = int(user_category + "00001")
    else:
        max_last_6_digits[user_category] = int(ipns_list[-1][-5:])

# Get the number of IPNs to generate from the user if not provided through terminal arguments
while True:
    try:
        if num_ipns_to_generate <= 0:
            num_ipns_to_generate = int(input(
                "Enter the number of IPNs to generate for this category (should be greater than 0): "))
        if num_ipns_to_generate > 0:
            break
        else:
            print("Please enter a positive integer greater than 0.")
    except ValueError:
        print("Invalid input. Please enter a positive integer greater than 0.")

num_generated = 0

# Sort the list of existing IPN numbers
ipns_list.sort()

# Initialize the index at the beginning of the list
i = 0

# Check if the first IPN in the list is greater than 1, if so, print it
first_ipn = int(ipns_list[0][6:11])
if first_ipn > 1:
    for ipn in range(1, first_ipn):
        next_ipn_str = str(ipn).rjust(5, '0')
        new_ipn = f"{user_category}{next_ipn_str}"
        print(f"Next available IPN for category {user_category}: {new_ipn}")
        num_generated += 1

while num_generated < num_ipns_to_generate and i < len(ipns_list) - 1:
    current_ipn = int(ipns_list[i][6:11])
    next_ipn = int(ipns_list[i + 1][6:11])

    if next_ipn - current_ipn > 1:
        # Calculate the sequence of available IPNs
        start_ipn = current_ipn + 1
        end_ipn = next_ipn - 1

        # Check if there are two or more consecutive available IPNs
        if end_ipn - start_ipn >= 1:
            for ipn in range(start_ipn, end_ipn + 1):
                next_ipn_str = str(ipn).rjust(5, '0')
                new_ipn = f"{user_category}{next_ipn_str}"
                print(
                    f"Next available IPN for category {user_category}: {new_ipn}")
                num_generated += 1
        else:
            # If there is only one available IPN, print it
            next_ipn_str = str(start_ipn).rjust(5, '0')
            new_ipn = f"{user_category}{next_ipn_str}"
            print(
                f"Next available IPN for category {user_category}: {new_ipn}")
            num_generated += 1

    i += 1

# If you generated fewer IPNs than requested, continue from where you left off
while num_generated < num_ipns_to_generate:
    max_existing_ipn = int(ipns_list[-1][6:11])
    next_ipn_str = str(max_existing_ipn + num_generated + 1).rjust(5, '0')
    new_ipn = f"{user_category}{next_ipn_str}"
    print(f"Next available IPN for category {user_category}: {new_ipn}")
    num_generated += 1

# Get the number of packaging needed from the user if not provided through terminal arguments
if num_packaging_needed <= 0:
    while True:
        try:
            num_packaging_needed = int(input(
                "Enter the number of packaging needed for this category (should be greater than 0): "))
            if num_packaging_needed > 0:
                break
            else:
                print("Please enter a positive integer greater than 0.")
        except ValueError:
            print("Invalid input. Please enter a positive integer greater than 0.")

# Read packagings from the JSON file for the selected category
packagings = [item["packaging"] for item in data if item.get(
    "packaging") and item.get("IPN").startswith(user_category)]

# Extract numbers from packagings and sort the list of numbers
numbers = []
text_after_number = ""  # Variable to store the text after the number

for packaging in packagings:
    try:
        num_str = packaging.split("N.")[-1].split()[0]
        num = int(num_str)
        # Extract the text after the number
        text_after_number = " ".join(packaging.split()[1:])
        numbers.append(num)
    except (IndexError, ValueError):
        pass

# Convert the numbers list to a set to remove duplicates and then back to a sorted list
numbers = sorted(set(numbers))

# Find the missing numbers in packagings
missing_packagings = []
for i in range(1, len(numbers)):
    diff = numbers[i] - numbers[i - 1]
    if diff > 1:
        for j in range(1, diff):
            missing_packaging = numbers[i - 1] + j
            missing_packagings.append(missing_packaging)

# Calculate the missing packaging numbers or generate them if none are available
if len(missing_packagings) < num_packaging_needed:
    # Calculate the number of missing packaging numbers needed
    num_missing_needed = num_packaging_needed - len(missing_packagings)

    # Find the maximum number among the existing numbers
    max_existing_number = numbers[-1] if numbers else 0

    # Generate the missing packaging numbers
    generated_missing_packagings = list(
        range(max_existing_number + 1, max_existing_number + 1 + num_missing_needed))

    # Extend the missing_packagings list with the generated numbers
    missing_packagings.extend(generated_missing_packagings)

# Print the requested missing numbers or generated missing numbers
if len(missing_packagings) >= num_packaging_needed:
    for i in range(num_packaging_needed):
        packaging_number = missing_packagings[i]
        print(
            f"Next available packaging for category {user_category}: N.{packaging_number} {text_after_number}")
else:
    print(f"All available missing packagings for category {user_category}:")
    for missing_packaging in missing_packagings:
        print(f"N.{missing_packaging} {text_after_number}")
