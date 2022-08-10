import companion_card_directory as ccd
import json
import os

remote_url = 'https://raw.githubusercontent.com/matthewproctor/australianpostcodes/master/australian_postcodes.json'
postcodes_dir = 'postcodes' + os.path.sep

if not os.path.exists(postcodes_dir):
    os.makedirs(postcodes_dir, exist_ok=True)
    
file = ccd.helpers.get_content_from_cache_or_remote(remote_url, ccd.helpers.get_data_dir() + postcodes_dir)
data = json.loads(file)

entries = {}
for record in data:
    state = record['state'].lower()

    entry = {
        'state': state,
        'postcode': record['postcode'],
        'region': record['SA3_NAME_2016']
    }

    if state not in entries.keys():
        entries[state] = {}

    entries[state][entry['postcode']] = entry

for state,entry in entries.items():
    print(state)
    print(postcodes_dir + state + '.json')
    ccd.helpers.write_json_file(postcodes_dir + state + '.json', entry)