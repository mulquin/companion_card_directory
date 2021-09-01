import companion_card_directory as ccd

states = ['nt', 'act']

for state in states:
    ccd.helpers.make_scrape_dir(state)
    scrape = getattr(ccd.scrape, state)
    scrape()