import requests

remote_url = 'https://raw.githubusercontent.com/matthewproctor/australianpostcodes/master/australian_postcodes.json'
local_file = 'data/postcodes.json'

data = requests.get(remote_url)

with open(local_file, 'wb') as file:
    file.write(data.content)

