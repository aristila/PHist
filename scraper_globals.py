#GLOBALS for web scraper PHist 1.1

#seedfile and name tag holders
seedfile = ''
language = ''
level = ''
prefix = ''

#These are stat holders
scraped_links = []
not_found = []
disallowed = []
robotstxt_not_found = []
seen_already = set()

#These are social media link holders
facebook_links = []
twitter_links = []
vk_links = []
linkedin_links = []


#Repository for links going to be scraped next
links_L2 = set()

