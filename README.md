# Companion Card Directory

>A python program that scrapes the Companion Card directories of the various states and territorities and puts it together

This project has two main objectives:

1. To unify the list of affiliates from the various state and territory Companion Card programs
2. To help me learn Python

## Dependencies

* Python3
* requests library for downloading
* BeautifulSoup for html parsing
* pdfplumber for PDF reader
* python-magic for mime type checking

Data is scraped from each state and territories list of affiliates

* [Australian Capital Territory](https://www.communityservices.act.gov.au/companion_card/affiliates)
* [New South Wales](https://www.nsw.gov.au/living-in-nsw/companion-card/use-card)
* [Northern Territory](https://ntcompanioncard.org.au/where-you-can-use-your-card)
* [Queensland](https://secure.communities.qld.gov.au/chiip/SearchBrowseCompanion.aspx)
* [South Australia](https://www.sa.gov.au/topics/care-and-support/disability/companion-card/using-your-companion-card)
* [Tasmania](https://www.companioncard.communities.tas.gov.au/affiliates/tasmanian_businesses_that_accept_the_companion_card)
* [Victoria](https://www.companioncard.vic.gov.au/where-can-i-use-my-card)
* [Western Australia](https://www.wacompanioncard.org.au/where-can-i-use-my-card)