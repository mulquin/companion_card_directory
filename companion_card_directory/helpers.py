import os
import time
import requests
import json
import magic

def update_log_file(state, entries, perf_time):
    with open('log.txt', 'a') as log:
        log.write(state + ' ' + str(entries) + ' ' + str(perf_time) + "\n")
    

def get_state_json(state):
    filename = get_data_dir() + state + '.json'
    file = open(filename)
    data = json.load(file)
    return data

def get_postcode_json(state):
    filename = get_data_dir() + 'postcodes' + os.path.sep + state + '.json'
    file = open(filename)
    data = json.load(file)
    return data

def write_json_file(filename, data):
    json_file = get_data_dir() + filename
    json_data = json.dumps(data, indent=4, sort_keys=True)
    #json_data = json.dumps(data, sort_keys=True)
    file = open(json_file, 'w').write(json_data)

def get_data_dir():
    return os.path.dirname(os.path.dirname(__file__)) + os.path.sep + 'data' + os.path.sep

def get_scrape_dir(state):
    return get_data_dir() + state + os.path.sep

def make_scrape_dir(state):
    scrape_dir = get_scrape_dir(state)

    if not os.path.exists(scrape_dir):
        os.makedirs(scrape_dir, exist_ok=True)

def get_content_from_cache_or_remote(remote_path, local_dir, is_index=False):
    remote_path = remote_path.rstrip('/')
    
    page_name = remote_path.rsplit('/', 1)[-1]

    remote_filename, remote_extension = os.path.splitext(page_name)

    page_name = "".join([c for c in remote_filename if c.isalpha() or c.isdigit() or c==' ']).rstrip()

    if (remote_extension == ''):
        extension = '.html'
    else:
        extension = remote_extension

    local_file = local_dir + page_name + extension
    
    should_dl = False

    if (os.path.isfile(local_file) == True):
        file_stat = os.stat(local_file)
        file_age = (time.time() - file_stat.st_mtime)
        if (file_age > 86400*3):
            should_dl = True
    else:
        should_dl = True

    if (should_dl == True):
        print('Downloading: ' + remote_path)
        request = requests.get(remote_path)

        with open(local_file, 'wb') as file:
            file.write(request.content)

        return request.content
    else:
        print('Cached: ' + local_file)
        mime = magic.Magic(mime=True)
        mimetype = mime.from_file(local_file)
        if (mimetype == 'application/pdf'):
            return open(local_file, 'rb')
        else:
            return open(local_file, 'r').read()