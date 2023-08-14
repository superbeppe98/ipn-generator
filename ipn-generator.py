import json

import sys
import os
from dotenv import load_dotenv
from inventree.api import InvenTreeAPI
from inventree.part import Part
from inventree.stock import StockItem

user_category = ""
num_ipns_to_generate = 0
num_packaging_needed = 0

if len(sys.argv) >= 2:
    user_category = sys.argv[1]
if len(sys.argv) >= 3:
    num_ipns_to_generate = int(sys.argv[2])
if len(sys.argv) >= 4:
    num_packaging_needed = int(sys.argv[3])

# Load environment variables from .env file
load_dotenv()

# Specify the path to the file containing URLs
path = "input.json"

# Clear the contents of the input and output files
with open(path, "w") as f:
    pass

# Create the file if it doesn't exist
if not os.path.exists(path):
    with open(path, "w") as f:
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

    # Prepare a list of dictionaries containing name, IPN, and ID for each part
    parts_data = []
    for part in parts:
        parts_data.append({
            "name": part.name,
            "IPN": part.IPN,
            "ID": part.pk,
            "packaging": "",  # Initialize the "packaging" field to empty
        })

    # Retrieve all stock items through the API
    stock_items = StockItem.list(api)

    # Update the JSON with the "packaging" field from the StockItems API
    for item in parts_data:
        part_ipn = item['IPN']

        # Find the part object that matches the current IPN
        part_obj = next((part for part in parts if part.IPN == part_ipn), None)

        if part_obj:
            # Get the list of stock items for the current part using its part.pk attribute
            stock_items_for_part = [
                stock_item for stock_item in stock_items if stock_item.part == part_obj.pk]

            if stock_items_for_part:
                # For simplicity, we'll assume only one stock item exists for each part
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

# Initialize an empty dictionary to track IPNs used in each category
used_ipns = {}

# Loop through all elements in the JSON file
for item in data:

    # Extract the IPN code as an integer
    ipn_code = item['IPN'].strip()

    # Extract the first 6 numbers of the IPN code, which represent the category
    ipn_code = str(ipn_code).rjust(11, '0')
    category = ipn_code[:6].replace(' ', '0')

    # Add the IPN code to the dictionary of codes used in the current category
    if category in used_ipns:
        used_ipns[category].add(ipn_code)
    else:
        used_ipns[category] = set([ipn_code])

# Calculate the maximum value of the last 5 digits of IPNs for each category
max_last_5_digits = {}
for category, ipns in used_ipns.items():
    max_last_5_digits[category] = max(int(ipn[-5:]) for ipn in ipns)

# Get the category from the user if not provided through terminal arguments
if not user_category:
    user_category = input(
        "Enter the category for which you want to generate the next IPN: ")

# Check if the category exists in the "used_ipns" dictionary
if user_category in used_ipns:
    ipns_list = sorted(list(used_ipns[user_category]))
    if len(ipns_list) == 0:
        max_last_5_digits[user_category] = int(user_category + "00001")
    else:
        max_last_5_digits[user_category] = int(ipns_list[-1][-5:])

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
    if len(ipns_list) > 1:
        for i in range(len(ipns_list)-1):
            diff = int(ipns_list[i+1][-5:]) - int(ipns_list[i][-5:])
            if diff > 1:
                next_ipn = str(int(ipns_list[i][-5:])+1).rjust(5, '0')
                new_ipn = f"{user_category}{next_ipn}"
                print(
                    f"Next available IPN for category {user_category}: {new_ipn}")
                num_generated += 1
                if num_generated >= num_ipns_to_generate:
                    break
        if num_generated >= num_ipns_to_generate:
            print()
        else:
            max_digits = int(ipns_list[-1][-5:])
            for i in range(num_generated, num_ipns_to_generate):
                next_ipn = str(max_digits + i + 1).rjust(5, '0')
                new_ipn = f"{user_category}{next_ipn}"
                print(
                    f"Next available IPN for category {user_category}: {new_ipn}")
            print()
    else:
        max_digits = int(ipns_list[-1][-5:])
        for i in range(num_ipns_to_generate):
            next_ipn = str(max_digits + i + 1).rjust(5, '0')
            new_ipn = f"{user_category}{next_ipn}"
            print(
                f"Next available IPN for category {user_category}: {new_ipn}")
        print()

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

# Print the requested missing numbers
if len(missing_packagings) >= num_packaging_needed:
    for i in range(num_packaging_needed):
        packaging_number = missing_packagings[i]
        print(
            f"Next available packaging for category {user_category}: N.{packaging_number} {text_after_number}")
else:
    print(f"All available missing packagings for category {user_category}:")
    for missing_packaging in missing_packagings:
        print(f"N.{missing_packaging} {text_after_number}")
