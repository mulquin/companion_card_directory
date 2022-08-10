import companion_card_directory as ccd
import time

states = ['nt', 'act', 'nsw', 'qld', 'wa', 'sa', 'tas', 'vic']

ccd.helpers.update_log_file('start', 0, time.perf_counter())
print('beginning scrape')
entries = []

for state in states:
    ccd.helpers.make_scrape_dir(state)
    scrape = getattr(ccd.scrape, state)
    scrape()

    data = ccd.helpers.get_state_json(state)

    for record in data:
        entry = {
            'state': state,
            'address': '',
            'category': '',
            'name': '',
            'phone': '',
            'website': '',
            'state_region': '',
            'email': '',
            'facebook': '',
            'instagram': '',
            'twitter': ''
        }

        if 'address' in record.keys():
            entry["address"] = record['address']
        
        if 'category' in record.keys():
            entry["category"] = record['category']

        if 'name' in record.keys():
            entry["name"] = record['name']

        if 'phone' in record.keys():
            entry["phone"] = record['phone']

        if 'website' in record.keys():
            entry["website"] = record['website']
        
        if 'state_region' in record.keys():
            entry["state_region"] = record['state_region']

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