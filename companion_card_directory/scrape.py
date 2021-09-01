import helpers
from bs4 import BeautifulSoup

def act():
    scrape_dir = helpers.get_scrape_dir('act')
    remote_index = 'https://www.communityservices.act.gov.au/companion_card/affiliates/'

    index_html = helpers.get_content_from_cache_or_remote(remote_index, scrape_dir)

    soup = BeautifulSoup(index_html, 'html.parser')

    main_div = soup.find('div', id='new_div_78258_78258')

    affiliate_links = main_div.find_all('a')

    for affiliate_link in affiliate_links:
        html = helpers.get_content_from_cache_or_remote(affiliate_link['href'], scrape_dir)

def nt():
    scrape_dir = helpers.get_scrape_dir('nt')
    remote_url = 'https://nt.gov.au/wellbeing/disability-services/nt-companion-card/where-you-can-use-your-card'
    html = helpers.get_content_from_cache_or_remote(remote_url, helpers.get_scrape_dir(scrape_dir))

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