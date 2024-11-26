import csv
import json
import pprint

def flatten_dict(d):
    flattened = {}
    for key, value in d.items():
        if isinstance(value, dict):
            flattened.update(flatten_dict(value))
        else:
            flattened[key] = value
    return flattened

with open('./data.json', 'r') as file:
    all_data = json.load(file)

key_categories = ['landlord', 'product_info_number', 'product_info']
all_field = []

# Find all field can exists
for index, data in enumerate(all_data):
    for key_category in key_categories:
        for key, value in data[key_category].items():
            if key not in all_field:
                all_field.append(key)

    all_data[index] = flatten_dict(data)

with open('data.csv', 'w') as file:
    writer = csv.DictWriter(file, fieldnames=all_field)

    writer.writeheader()

    writer.writerows(all_data)