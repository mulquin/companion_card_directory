import os
import time
import requests
import json
import magic

def write_json_file(filename, data):
    json_file = get_data_dir() + filename
    json_data = json.dumps(data, indent=4, sort_keys=True)
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
    page_name = remote_path.rsplit('/', 1)[-1]
    page_name = "".join([c for c in page_name if c.isalpha() or c.isdigit() or c==' ']).rstrip()

    if (page_name == ''):
        local_file = local_dir + '_index.html' # Increment if seen before
    elif (is_index == True):
        local_file = local_dir + '_'+page_name + '.html'
    else:
        local_file = local_dir + page_name + '.html' #Add support for files that already end in .html
    
    should_dl = False

    if (os.path.isfile(local_file) == True):
        file_stat = os.stat(local_file)
        file_age = (time.time() - file_stat.st_mtime)
        if (file_age > 86400):
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