import companion_card_directory as ccd
import time
states = ['nt', 'act', 'nsw', 'qld', 'wa', 'sa', 'tas', 'vic']

ccd.helpers.update_log_file('start', 0, time.perf_counter())
print('beginning scrape')
for state in states:
    ccd.helpers.make_scrape_dir(state)
    scrape = getattr(ccd.scrape, state)
    scrape()
