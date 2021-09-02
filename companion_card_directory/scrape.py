import helpers
from bs4 import BeautifulSoup
import pdfplumber

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

def nt():
    print('nt')
    scrape_dir = helpers.get_scrape_dir('nt')
    remote_url = 'https://nt.gov.au/wellbeing/disability-services/nt-companion-card/where-you-can-use-your-card'
    html = helpers.get_content_from_cache_or_remote(remote_url, scrape_dir)

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

    helpers.write_json_file('nt.json', data)

def nsw():
    print('nsw')
    scrape_dir = helpers.get_scrape_dir('nsw')
    remote_url = 'https://www.companioncard.nsw.gov.au/cardholders/where-can-i-use-my-card'

    html = helpers.get_content_from_cache_or_remote(remote_url, scrape_dir, True)

    data = []

    affiliate_links = []

    soup = BeautifulSoup(html, 'html.parser')

    link_list = soup.select('ul#ul-646007 span.bold a')

    for link in link_list:
        affiliate_links.append(link['href'])

    while True:
        go_next = ''
        next_link = soup.select('div.inline-block.width-20.mobile-width-50.no-mobile.align-right a')

        if (next_link == None):
            break

        if (len(next_link) == 0):
            break
        
        go_next = next_link[0]['href']

        html = helpers.get_content_from_cache_or_remote(go_next, scrape_dir, True)

        soup = BeautifulSoup(html, 'html.parser')

        link_list = soup.select('ul#ul-646007 span.bold a')

        for link in link_list:
            affiliate_links.append(link['href'])

    for link in affiliate_links:
        html = helpers.get_content_from_cache_or_remote(link, scrape_dir)
        soup = BeautifulSoup(html, 'html.parser')

        paragraphs = soup.select('#readable-content p')
        
        name = soup.find('h1').get_text();
        category = ''
        address = ''
        phone = ''
        website = ''
        description = ''

        description = paragraphs[0].get_text()
        for paragraph in paragraphs:
            strong = paragraph.find('strong')
            if (hasattr(strong, 'get_text')):
                field = strong.get_text()
                if (field == "Business type"):
                    category = strong.next_sibling.next_sibling
                    if (category == None):
                        category = soup.select('div.breadcrumbs li:last-of-type a')[0].get_text()
                        print("\tUsing breadcrumb for category")
                elif (field == "Phone number"):
                    phone = strong.next_sibling.next_sibling
                elif (field == "Address"):
                    address = strong.next_sibling.next_sibling.get_text().strip()
                elif (field == "Website"):
                    website = strong.next_sibling.next_sibling['href']
                else:
                    print ('Unknown field: "' + field + '"')
       
        entry = {
            'category': category,
            'name': name,
            'address': address,
            'phone': phone,
            'website': website,
            'description': description
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
    remote_url = 'https://www.wacompanioncard.org.au/where-can-i-use-my-card'

    html = helpers.get_content_from_cache_or_remote(remote_url, scrape_dir, True)

    data = []

    affiliate_links = []

    soup = BeautifulSoup(html, 'html.parser')

    link_list = soup.select('#itemListLinks a')

    for link in link_list:
        built_link = 'https://www.wacompanioncard.org.au' + link['href']
        affiliate_links.append(built_link)

    while True:
        go_next = ''
        next_link = soup.select('li a.next')

        if (next_link == None):
            break

        if (len(next_link) == 0):
            break
        
        go_next = 'https://www.wacompanioncard.org.au' + next_link[0]['href']

        html = helpers.get_content_from_cache_or_remote(go_next, scrape_dir, True)

        soup = BeautifulSoup(html, 'html.parser')

        link_list = soup.select('#itemListLinks a')

        for link in link_list:
            built_link = 'https://www.wacompanioncard.org.au' + link['href']
            affiliate_links.append(built_link)

    for link in affiliate_links:
        html = helpers.get_content_from_cache_or_remote(link, scrape_dir)
        soup = BeautifulSoup(html, 'html.parser')

        name = soup.select('h2.itemTitle')[0].get_text().strip()
 
        fields = soup.select('div.itemExtraFields li')

        for field in fields:
            field_name = field.find_all('span')[0].get_text().strip()

            if (field_name == 'Type/Category:'):
                category = field.find_all('span')[1].get_text()
            elif (field_name == 'Street Address:'):
                street = field.find_all('span')[1].get_text()
            elif (field_name == 'Suburb:'):
                suburb = field.find_all('span')[1].get_text()
            elif (field_name == 'State:'):
                state = field.find_all('span')[1].get_text()
            elif (field_name == 'Postcode:'):
                postcode = field.find_all('span')[1].get_text()
            elif (field_name == 'Phone Number:'):
                phone = field.find_all('span')[1].get_text()
                if (phone == '.'):
                    phone = ''
            elif (field_name == 'Website:'):
                website = ''
                if (field.find('a') != None):
                    website = field.find('a')['href']
            else:
                print('wtf field: ' + field_name)

        address = street + ", " + suburb + ", " + state + ", " + postcode

        description = soup.select('div.itemFullText')[0].get_text().strip()

        entry = {
            'category': category,
            'name': name,
            'address': address,
            'phone': phone,
            'website': website,
            'description': description
        }

        data.append(entry)
    
    helpers.write_json_file('wa.json', data)
    
def tas():
    print ('tas')
    scrape_dir = helpers.get_scrape_dir('tas')
    remote_url = 'https://www.companioncard.communities.tas.gov.au/affiliates/tasmanian_businesses_that_accept_the_companion_card'
    html = helpers.get_content_from_cache_or_remote(remote_url, scrape_dir)

    soup = BeautifulSoup(html, 'html.parser')

    paragraphs = soup.select('#main-content p:nth-child(n+7)')

    data = []

    for paragraph in paragraphs:
        strong = paragraph.find('strong')
        name = strong.get_text()
        
        website = ''

        link = strong.find('a')
        if (link != None):
            website = link['href']


        entry = {
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

    pdf = pdfplumber.open(file)
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
