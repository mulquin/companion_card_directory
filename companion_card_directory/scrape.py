import helpers
from bs4 import BeautifulSoup

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

def qld():
    print('qld')

def vic():
    print ('vic')

def wa():
    print ('wa')

def sa():
    print ('sa')

def tas():
    print ('tas')