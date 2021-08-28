import os
import time
import requests
import json
from bs4 import BeautifulSoup

root_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir)) + os.path.sep
data_dir = root_dir + 'data' + os.path.sep + 'nt' + os.path.sep

if not os.path.exists(data_dir):
    os.makedirs(data_dir)

remote_url = 'https://nt.gov.au/wellbeing/disability-services/nt-companion-card/where-you-can-use-your-card'
local_file = data_dir + 'index.html'

should_dl = False

if (os.path.isfile(local_file) == True):
    file_stat = os.stat(local_file)
    file_age = (time.time() - file_stat.st_mtime)
    if (file_age > 60*60*24):
        should_dl = True
else:
    should_dl = True


if (should_dl == True):
    request = requests.get(remote_url)

    with open(local_file, 'wb') as file:
        file.write(request.content)

    html = request.content
else:
    html = open(local_file, 'r').read()

data = []

soup = BeautifulSoup(html, 'html.parser')

accordions = soup.find_all('div', class_='tmp_accordion')

for accordion in accordions:
    category = accordion.find('a', class_='btn').get_text()
    entries = accordion.select('tbody tr')

    for entry in entries:

        cells = entry.select('td')

        cells_len = len(cells)

        if (cells_len == 3): # Events and Festivals do not have fixed address
            entry = {
                'category': category,
                'name': cells[0].get_text().strip(),
                'address': '',
                'phone': cells[1].get_text().strip(),
                'website': cells[2].find('a')['href'].strip()
            }
        else:
            entry = {
                'category': category,
                'name': cells[0].get_text().strip(),
                'address': cells[1].get_text().strip(),
                'phone': cells[2].get_text().strip(),
                'website': cells[3].find('a')['href'].strip()
            }

        data.append(entry)

json_file = root_dir + 'data' + os.path.sep + 'nt.json'

json = json.dumps(data, indent=4, sort_keys=True)

file = open(json_file, 'w').write(json)