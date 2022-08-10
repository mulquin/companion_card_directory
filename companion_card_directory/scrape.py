import helpers
from bs4 import BeautifulSoup
import pdfplumber
import json
import requests
import os
import time
import re

def act_get_next_sibling_text(soup, paragraphs, strong_text):
    for paragraph in paragraphs:
        strong = paragraph.find("strong", text=strong_text)
        if (hasattr(strong, 'next_sibling')):
            return strong.next_sibling.strip()
        
        strong_with_space = paragraph.find("strong", text=strong_text+" ")
        if (hasattr(strong_with_space, 'next_sibling')):
            return strong_with_space.next_sibling.strip()

    return ''

def act_get_next_sibling_href(soup, paragraphs, strong_text):
    for paragraph in paragraphs:
        strong = paragraph.find("strong", text=strong_text)
        has_get_next = getattr(strong, "find_next", None)
        if callable(has_get_next):
            a = strong.find_next('a')
            return a['href']

        strong = paragraph.find("strong", text=strong_text+" ")
        has_get_next = getattr(strong, "find_next", None)
        if callable(has_get_next):
            a = strong.find_next('a')
            return a['href']

    return ''

def act():
    print('act')
    scrape_dir = helpers.get_scrape_dir('act')
    remote_index = 'https://www.communityservices.act.gov.au/companion_card/affiliates/'

    index_html = helpers.get_content_from_cache_or_remote(remote_index, scrape_dir)

    soup = BeautifulSoup(index_html, 'html.parser')

    main_div = soup.find('div', id='new_div_78258_78258')

    affiliate_links = main_div.find_all('a')

    data = []

    for affiliate_link in affiliate_links:
        html = helpers.get_content_from_cache_or_remote(affiliate_link['href'], scrape_dir)
        
        soup = BeautifulSoup(html, 'html.parser')

        paragraphs = soup.select("#main p")

        num_paragraphs = len(paragraphs)

        mailtos = soup.select('#main a[href^=mailto]')
        email = ''
        if len(mailtos) == 1:
            email = mailtos[0]['href'].split(":")[1]

        entry = {
            'name': soup.find('h1').get_text(),
            'address': '',
            'phone': '',
            'website': '',
            'email': email,
            'facebook': '',
            'instagram': '',
            'twitter': '',
        }     

        if (num_paragraphs > 2):
            entry['address'] = paragraphs[0].get_text(separator=", ")
        
        entry['phone'] = act_get_next_sibling_text(soup, paragraphs, 'Ph:')
        entry['website'] = act_get_next_sibling_href(soup, paragraphs, 'Web:')
        entry['facebook'] = act_get_next_sibling_href(soup, paragraphs, 'Facebook:')
        entry['instagram'] = act_get_next_sibling_href(soup, paragraphs, 'Instagram:')
        entry['twitter'] = act_get_next_sibling_href(soup, paragraphs, 'Twitter:')

        data.append(entry)

    helpers.write_json_file('act.json', data)

def nt_extract_item(item, category):
    name = item.find('h2').get_text()
    website = ''
    button = item.select('.fl-button')
    if (len(button) > 0):
        website = item.select('.fl-button')[0]['href']
    
    description = ''
    email = ''
    phone = ''
    address = ''

    paragraphs = item.select('p')
    for p in paragraphs:
        if p.get_text() != '' and p.find('p') == None:
            p_text = p.get_text()
            if "Address:" in p_text:
                address = p_text.split('Address:')[1].strip()
            elif "Phone:" in p_text:
                phone = p_text.split('Phone:')[1].strip()
            elif "Email:" in p_text:
                email = p_text.split('Email:')[1].strip()
            else:
                description = p_text.strip()
            
    return {
        'category': category,
        'name': name,
        'address': address,
        'phone': phone,
        'website': website
    }

def nt():
    print('nt')
    scrape_dir = helpers.get_scrape_dir('nt')
    remote_url = 'https://ntcompanioncard.org.au/where-you-can-use-your-card'
    html = helpers.get_content_from_cache_or_remote(remote_url, scrape_dir)

    data = []

    soup = BeautifulSoup(html, 'html.parser')

    categories = soup.select('.searchandfilter ul li:nth-of-type(2) ul li')

    for cat in categories:
        category = cat.find('label').get_text()
        id = cat.find('input')['value']
        if (category == 'All Venues'):
            continue
        category = category.split('(')[0]
        url = 'https://ntcompanioncard.org.au/?sfid=640&sf_action=get_data&sf_data=all&_sft_venue_type='+id+'&lang=en'


        response = helpers.get_content_from_cache_or_remote(url, scrape_dir)
        
        form_results = json.loads(response)
        results = form_results['results']

        soup = BeautifulSoup(results, 'html.parser')
        items = soup.select('.affiliates')

        for item in items:
            entry = nt_extract_item(item, category)
            data.append(entry)    

        while True:
            go_next = ''
            next_link = soup.select('.pagination .nav-previous a')

            if (next_link == None):
                break

            if (len(next_link) == 0):
                break
            
            go_next = next_link[0]['href']

            html = helpers.get_content_from_cache_or_remote(go_next, scrape_dir, True)

            soup = BeautifulSoup(html, 'html.parser')

            items = soup.select('.affiliates')

            for item in items:
                entry = nt_extract_item(item, category)
                data.append(entry)

    helpers.write_json_file('nt.json', data)

def nsw_get_listings_from_cache_or_remote():
    scrape_dir = helpers.get_scrape_dir('nsw')
    local_file = scrape_dir + 'data.json'

    should_dl = False

    if (os.path.isfile(local_file) == True):
        file_stat = os.stat(local_file)
        file_age = (time.time() - file_stat.st_mtime)
        if (file_age > 86400*3):
            should_dl = True
    else:
        should_dl = True

    if (should_dl == True):
        print('Downloading: https://www.nsw.gov.au/living-in-nsw/companion-card/use-card')

        data = {"query":{"function_score":{"query":{"bool":{"must":[{"match":{"type":"poi"}},{"match":{"subtype":"affiliatedbusiness"}},{"bool":{"should":[]}},{"bool":{"should":[]}}]}},"random_score":{}}}}

        response = requests.post(
            url='https://www.nsw.gov.au/api/v1/elasticsearch/prod_content/_search?size=9000',
            headers={
                'Content-Type': 'application/json',
                'Referer': 'https://www.nsw.gov.au/living-in-nsw/companion-card/use-card'
            },
            data=json.dumps(data)
        )

        with open(local_file, 'w') as file:
            file.write(response.text)

        return json.loads(response.text)

    else:
        print('Cached: ' + local_file)
        return json.loads(open(local_file, 'r').read())

# from https://stackoverflow.com/a/67579534/1427345
def nsw_extract_dl(soup):
    keys, values = [], []
    for dt in soup.findAll("dt"):
        keys.append(dt.text.strip())
    for dd in soup.findAll("dd"):
        values.append(dd.text.strip())
    return dict(zip(keys, values))

def nsw():
    print('nsw')
    scrape_dir = helpers.get_scrape_dir('nsw')

    json_data = nsw_get_listings_from_cache_or_remote() 

    data = []

    for item in json_data['hits']['hits']:
        source = item['_source']

        listing_url = 'https://www.nsw.gov.au' + source['url'][0]

        html = helpers.get_content_from_cache_or_remote(listing_url, scrape_dir)

        soup = BeautifulSoup(html, 'html.parser')

        div = soup.select('.node-section-content div')[0]
        dl = div.find('dl')

        content = nsw_extract_dl(dl)

        address = re.sub('\s+',' ',content['Address'].replace(" \n", ","))

        phone = ''
        if 'Phone' in content:
            phone = content['Phone']

        website = ''
        if 'Website' in content:
            website = content['Website']

        entry = {
            'category': source['name_industry'][0],
            'name': source['title'][0],
            'address': address,
            'phone': phone,
            'website': website,
            'description': source['summary'][0],
            'state_region': source['name_region'][0]
        }

        data.append(entry)

    helpers.write_json_file('nsw.json', data)
    
def qld():
    print('qld')
    scrape_dir = helpers.get_scrape_dir('qld')
    remote_url = 'https://secure.communities.qld.gov.au/chiip/SearchBrowseCompanion.aspx'

    html = helpers.get_content_from_cache_or_remote(remote_url, scrape_dir, True)

    data = []

    category_links = []

    soup = BeautifulSoup(html, 'html.parser')

    category_links_pages = soup.select('#content ol a')

    for category_links_page in category_links_pages:
        category_links.append("https://secure.communities.qld.gov.au/chiip/" + category_links_page['href'])

    for category_link in category_links:
        html = helpers.get_content_from_cache_or_remote(category_link, scrape_dir, True)
        
        soup = BeautifulSoup(html, 'html.parser')
        affiliates = soup.select('#custombody li')
        
        for affiliate in affiliates:
            name = affiliate.select('span[id$=VenueName]')[0].get_text()
            category = affiliate.select('span[id$=BusCat]')[0].get_text()
            street = affiliate.select('span[id$=Addr1]')[0].get_text()
            suburb = affiliate.select('span[id$=Suburb]')[0].get_text()
            address = street + ", " + suburb
            phone = affiliate.select('span[id$=ContactPh]')[0].get_text()
            website = affiliate.find('a')['href']

            entry = {
                'category': category,
                'name': name,
                'address': address,
                'phone': phone,
                'website': website
            }
            
            data.append(entry)

        while True:
            go_next = ''
            next_link = soup.select('#custombody p:last-of-type a:nth-last-of-type(2)')

            if (len(next_link) == 0):
                break

            if (next_link[0].get_text() != '>'):
                break

            go_next = "https://secure.communities.qld.gov.au" + next_link[0]['href']

            html = helpers.get_content_from_cache_or_remote(go_next, scrape_dir, True)

            soup = BeautifulSoup(html, 'html.parser')

            affiliates = soup.select('#custombody li')
        
            for affiliate in affiliates:
                name = affiliate.select('span[id$=VenueName]')[0].get_text()
                category = affiliate.select('span[id$=BusCat]')[0].get_text()
                street = affiliate.select('span[id$=Addr1]')[0].get_text()
                suburb = affiliate.select('span[id$=Suburb]')[0].get_text()
                address = street + ", " + suburb
                phone = affiliate.select('span[id$=ContactPh]')[0].get_text()
                website = affiliate.find('a')['href']

                entry = {
                    'category': category,
                    'name': name,
                    'address': address,
                    'phone': phone,
                    'website': website
                }
                
                data.append(entry)
                
    helpers.write_json_file('qld.json', data)

def wa():
    print ('wa')
    scrape_dir = helpers.get_scrape_dir('wa')
    remote_url = 'https://www.wacompanioncard.org.au/affiliates_dir_ltg-sitemap.xml'

    xml = helpers.get_content_from_cache_or_remote(remote_url, scrape_dir, True)

    soup = BeautifulSoup(xml, 'lxml-xml')

    locs = soup.find_all('loc')

    data = []

    for loc in locs:
        if (loc.prefix == 'image'):
            continue

        url = loc.get_text()

        html = helpers.get_content_from_cache_or_remote(url, scrape_dir, True)

        soup = BeautifulSoup(html, 'html.parser')

        name = soup.find('h1').get_text()

        cats = soup.select('div[data-name="entity_field_directory_category"] a')
        cat_names = []
        for cat in cats:
            cat_names.append(cat.get_text())

        category = ", ".join(cat_names)

        description = ''
        soup_desc = soup.select('div[data-name="entity_field_post_content"]')
        if (len(soup_desc) > 0):
            description = soup_desc[0].get_text().strip()

        address = ''
        soup_addr = soup.select('div[data-name="entity_field_location_address"] span')
        if (len(soup_addr) > 0):
            address = soup_addr[0].get_text().strip().replace(' , ', ', ')

        phone = ''
        soup_phone = soup.select('div[data-name="entity_field_field_phone"] a')
        if (len(soup_phone) > 0):
            phone = soup_phone[0].get_text()

        email = ''
        soup_email = soup.select('div[data-name="entity_field_field_email"] a')
        if (len(soup_email) > 0):
            email = soup_email[0].get_text()

        website = ''
        soup_web = soup.select('div[data-name="entity_field_field_website"] a')
        if (len(soup_web) > 0):
            website = soup_web[0].get_text()

        entry = {
            'category': category,
            'name': name,
            'address': address,
            'phone': phone,
            'website': website,
            'description': description
        }

        data.append(entry)
        
       
def tas():
    print ('tas')
    scrape_dir = helpers.get_scrape_dir('tas')
    remote_url = 'https://www.companioncard.communities.tas.gov.au/affiliates/directory'
    html = helpers.get_content_from_cache_or_remote(remote_url, scrape_dir)

    soup = BeautifulSoup(html, 'html.parser')

    ul = soup.select('#main-content ul')[0]

    categories = ul.select('li')

    data = []

    for cat in categories:
        category = cat.get_text()
        url = cat.find('a')['href']
        
        html = helpers.get_content_from_cache_or_remote(url, scrape_dir)
        
        soup = BeautifulSoup(html, 'html.parser')

        ul = soup.select('#main-content ul')[0]
        items = ul.select('li')

        for item in items:

            name = item.find('strong').get_text()
            website = ''

            link = item.find('a')
            if (link != None):
                website = link['href']

            entry = {
                'category': category,
                'name': name,
                'website': website
            }

            data.append(entry)

    helpers.write_json_file('tas.json', data)

def vic():
    print ('vic')
    scrape_dir = helpers.get_scrape_dir('vic')
    remote_url = 'https://www.companioncard.vic.gov.au/sites/default/files/documents/202101/Companion%20Card%20Affiliates%20List_postcode.pdf'
    file = helpers.get_content_from_cache_or_remote(remote_url, scrape_dir)

    pdf = pdfplumber.open(file, password="")
    data = []

    for page in pdf.pages:
        table = page.extract_table()
        if (table == None):
            continue

        for rows in table:
            name = rows[0]
            if (name == 'Business Name'):
                continue

            address = '';
            if (rows[1] != None):
                address += rows[1]
            if (rows[2] != None):
                address += ", " + rows[2]
            if (rows[3] != None):
                address += ", " + rows[3]

            description = ''
            if (rows[4] != None):
                description = rows[4].replace("\n", " ")
                 
            entry = {
                'name': rows[0],
                'address': address,
                'description': description.replace("\n", " ")
            }
            data.append(entry)
    
    helpers.write_json_file('vic.json', data)

def sa():
    print ('sa')
    scrape_dir = helpers.get_scrape_dir('sa')
    remote_url = 'https://www.sa.gov.au/topics/care-and-support/disability/companion-card/using-your-companion-card'
    html = helpers.get_content_from_cache_or_remote(remote_url, scrape_dir)

    soup = BeautifulSoup(html, 'html.parser')

    link = soup.select('a[title="SA Companion Card Affiliate List"]')

    pdf_url = link[0].get('href')
    
    file = helpers.get_content_from_cache_or_remote(pdf_url, scrape_dir)

    pdf = pdfplumber.open(file, password="")

    data = []

    pages = pdf.pages

    for i,pg in enumerate(pages):
        if (i == 0 or i == 1):
            continue
        text = pages[i].extract_text()
        text = text.replace("APC I051 | July 2021", "")
        text = text.replace("We would like to acknowledge the generous support of the \nfollowing venues and events that have agreed to accept the \nCompanion Card.","")
        lines = text.split("\n")
        
        lines = [l.strip() for l in lines]
        lines = [l for l in lines if l]

        del lines[0]
        lines.pop()

        current_dot = 0
        last_dot = 0

        for j, line in enumerate(lines):
            if (len(line) == 1):
                del lines[j]

            lines[j] = lines[j].replace('•', '').strip()

            entry = {
                'name': lines[j]
            }

            data.append(entry)

    helpers.write_json_file('sa.json', data)