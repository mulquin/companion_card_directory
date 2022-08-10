import companion_card_directory as ccd
import time
import re
import json
import csv

states = ['nt', 'act', 'nsw', 'qld', 'wa', 'sa', 'tas', 'vic']

ccd.helpers.update_log_file('start', 0, time.perf_counter())
print('beginning scrape')
entries = []

for state in states:
    ccd.helpers.make_scrape_dir(state)
    scrape = getattr(ccd.scrape, state)
    scrape()

# FIXME: Do this without double loop
for state in states:

    postcodes = ccd.helpers.get_postcode_json(state) 
    data = ccd.helpers.get_state_json(state)

    for record in data:
        entry = {
            'state': state,
            'address': '',
            'category': '',
            'name': '',
            'phone': '',
            'website': '',
            'region': '',
            'email': '',
            'facebook': '',
            'instagram': '',
            'twitter': ''
        }

        if 'address' in record.keys():
            entry["address"] = record['address']

            numbers = re.findall('\d{4}$', record['address'])

            if len(numbers) > 0:
                postcode = numbers[0]
                if postcode in postcodes:
                    region = postcodes[postcode]['region']
                    entry['region'] = region
        
        if 'category' in record.keys():
            entry["category"] = record['category']

        if 'name' in record.keys():
            entry["name"] = record['name']

        if 'phone' in record.keys():
            entry["phone"] = record['phone']

        if 'website' in record.keys():
            entry["website"] = record['website']

        if 'email' in record.keys():
            entry["email"] = record['email']

        if 'facebook' in record.keys():
            entry["facebook"] = record['facebook']

        if 'instagram' in record.keys():
            entry["instagram"] = record['instagram']

        if 'twitter' in record.keys():
            entry["twitter"] = record['twitter']

        entries.append(entry)

ccd.helpers.write_json_file('all.json', entries)
ccd.helpers.write_csv_file('all.csv', entries)