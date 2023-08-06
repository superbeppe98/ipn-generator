# IPN Generator
The IPN Generator is a Python program that generates unique internal reference numbers (IPNs) for different categories based on a set of rules. It takes a JSON input file containing data for different items and generates new IPNs for items that don't have one or have a duplicate IPN.

## Installation
To use the IPN Generator, you need to have Python 3 installed on your system. You also need to have the following packages installed: json, sys, os, dotenv, inventree.api, inventree.part, and inventree.stock. You can install these packages by running the following command in your terminal or command prompt:
```shell
pip install -r requirements.txt
```

## Usage
To use the IPN Generator, you need to create a JSON input file that contains the data for the items you want to generate IPNs for. The input file should have the following format:
```shell

[
    {    "Item Code": 3137,
        "Item Name": "10 Volumes The Great Discoveries of Archaeology",
        "Item Description": "Book",
        "IPN - Internal reference number": "00000100179",
        "Category ID": 9,
        "Category Name": "000001 - BOOKS",
        "Default Location ID": 2,
        "Active": "1",
        "In Stock": "1.00000",
        "Creation Date": "2023-03-05",
        "Creation User": 1,
        "Responsible": ""}
]

```
You can run the program by navigating to the directory where the program is stored and running the following command:
```shell
python3 ipn-generator.py [category] [num_ipns_to_generate] [num_packaging_needed]

```
- [category] (optional): The category for which you want to generate the next IPN. If not provided, the program will prompt for it.
- [num_ipns_to_generate] (optional): The number of IPNs to generate for the specified category. If not provided, the program will prompt for it.
- [num_packaging_needed] (optional): The number of packaging needed for each category. If not provided, the program will prompt for it.
The program will then generate and print the next available IPNs and packaging for the specified category.

Please note that the program relies on environment variables for the Inventree server address, username, and password. Make sure to set these variables in a .env file in the same directory as the script.

## Note
The example "input.json" file used in this script is generated by Inventree, an open-source inventory management system. You can learn more about Inventree on its [GitHub repository](https://github.com/inventree).
