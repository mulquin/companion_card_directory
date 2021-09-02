# Companion Card Directory

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

* Northern Territory: https://nt.gov.au/wellbeing/disability-services/nt-companion-card/where-you-can-use-your-card
* ACT: https://www.communityservices.act.gov.au/companion_card/affiliates
* Tasmania: https://www.companioncard.communities.tas.gov.au/affiliates/tasmanian_businesses_that_accept_the_companion_card
* Western Australia: https://www.wacompanioncard.org.au/where-can-i-use-my-card
* NSW: https://www.companioncard.nsw.gov.au/cardholders/where-can-i-use-my-card
* Queensland: https://secure.communities.qld.gov.au/chiip/SearchBrowseCompanion.aspx

* South Australia: https://www.sa.gov.au/__data/assets/pdf_file/0009/684828/I051-Companion-Card-Affiliate-List-07_2021.pdf
* Victoria: https://www.companioncard.vic.gov.au/where-can-i-use-my-card


The data is normalized into the following fields

* State
* SA4
* Business Name
* Category
* Address
* Phone Number
* Fax
* Email
* Webpage

## State specific oddities

## New South Wales

Directory has a limit of 1000, seems suspiciously like an artifical limit?

### Victoria

Directory is only available in PDF

### Queensland

### Western Australia

### South Australia

PDF only

Only has business names

### Tasmania

Tasmania's website only includes business name and website

### Northern Territory

Single page

### Australian Capital Territory

N/A
