#This is the library for the web scraper PHist 1.1

import requests, codecs, json, datetime
import robotexclusionrulesparser
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from collections import OrderedDict
import scraper_globals as sg




#Getting the seed links and cleaning them up a bit
def get_seeds(filename):
    seed_links = []
    with codecs.open(filename, 'r', encoding='utf-8-sig') as f: 
        seed_links = f.read().split('\r\n')
    seed_links = [w.replace(' ', '') for w in seed_links]
    return seed_links


#Checks if link has already been processed before
def check_seen(link):
    seen = False
    for item in sg.seen_already:
        if link == item:
            seen = True
            break
    return seen


#Creating file id
def numFile(iter_num):
    zero = '0'
    L = len(str(iter_num))
    file_num = ((6-L)*zero) + str(iter_num)
    return file_num


#Checking from ROBOTS.TXT if link is allowed to be scraped or not
def checkRobotstxt(link):
    #Creating link to ROBOTS.TXT
    urlparts = urlparse(link)
    robotstxt_link = urlparts[0] + '://' + urlparts[1] + '/' + 'robots.txt'
    #Checking scrapability
    answer = False
    err = False
    rerp = robotexclusionrulesparser.RobotExclusionRulesParser()
    # Set the (optional) user_agent before calling fetch.
    rerp.user_agent = 'PHist/1.0; https://sites.utu.fi/pseudohistoria/en/'
    user_agent = 'PHist/1.0; https://sites.utu.fi/pseudohistoria/en/'
    try:
        rerp.fetch(robotstxt_link)
        ans = rerp.is_allowed(user_agent, link)
        answer = ans
    except:
        err = True
    return answer, err


'''
#OLD ROBOTSPARSER,
#hangs on certain urls
import urllib.robotsparser
    try:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robotstxt_link)
        rp.read()
        answer = rp.can_fetch('*', link)
        err = False
    except:
        err = True
    return answer, err
'''


#Retreiving and parsing page contents for use
def soup(url, log):
    #The line below is how the crawler identities itself to the website
    user_agent = 'PHist/1.0; https://sites.utu.fi/pseudohistoria/en/'
    page_content = 0
    try:
        page_response = requests.get(url, timeout=7, headers={"user-agent": user_agent})
        page_content = BeautifulSoup(page_response.content, "html.parser")
    except requests.exceptions.ConnectionError:
        print('     Connection error / no page content found.', file = log)
        log.flush()
        page_content = 1
        pass
    except:
        print('     Something went wrong / no page content found.', file = log)
        log.flush()
        pass
    return page_content


#Collecting scrape date
def scr_date(log):
    now = datetime.datetime.now()
    scrape_date = now.strftime("%Y-%m-%d %H:%M:%S")
    print('     Scrape time stamp: ' + scrape_date, file = log)
    return scrape_date


#Converts Russian month names into numbers
def month_conversion(string):
    k = ''
    v = ''
    rusmonths = {
        'январь' : '1',
        'февраль' : '2',
        'март' : '3',
        'апрель' : '4',
        'май' : '5',
        'июнь' : '6',
        'июль': '7',
        'август' : '8',
        'сентябрь' : '9',
        'октябрь' : '10',
        'ноябрь' : '11',
        'декабрь' : '12',
        'января' : '1',
        'февраля' : '2',
        'марта' : '3',
        'апреля' : '4',
        'мая' : '5',
        'июня' : '6',
        'июля' : '7',
        'августа' : '8',
        'сентября' : '9',
        'октября' : '10',
        'ноября' : '11',
        'декабря' : '12'
        }

    for key in rusmonths:
        if key in string:
            k = key
            v = rusmonths.get(key)
            break
    
    return k, v



#Collecting text publish date (only works on certain domains!)
def pub_date(page_content, url, log):
    date = 'unknown'
    if 'ari.ru' in url:
        try:
            d = page_content.find('div', class_='article-date').text
            datetime_object = datetime.datetime.strptime(d, '%d/%m/%Y %H:%M')
            date = datetime_object.strftime("%Y-%m-%d %H:%M")
        except:
            print('     Could not find ARI publish date.', file = log)
    elif 'pandoraopen.ru' in url:
        try:
            d = page_content.find('div', id='stats')
            d2 = d.span.text
            rusm, numm = month_conversion(d2)
            d3 = d2.replace(str(rusm), str(numm))
            datetime_object = datetime.datetime.strptime(d3, '%H:%M. %d %m %Y')
            date = datetime_object.strftime("%Y-%m-%d %H:%M")
        except:
            print('     Could not find PANDORAOPEN publish date.', file = log)
    elif 'liveinternet.ru' in url:
        try:
            d = page_content.find('span', class_='GL_TXTSM GL_MAR5B')
            d2 = d.text
            comma = d2.find(',')
            colon = d2.find(':')
            d3 = d2[comma:(colon+3)]
            d3 = d3.lower()
            rusm, numm = month_conversion(d3)
            d4 = d3.replace(str(rusm), str(numm))
            datetime_object = datetime.datetime.strptime(d4, ', %d %m %Y г. %H:%M')
            date = datetime_object.strftime("%Y-%m-%d %H:%M")
        except:
            print('     Could not find LIVEINTERNET publish date.', file = log)
    elif 'livejournal.com' in url:
        try:
            d = page_content.find('time')
            d2 = d.text
            datetime_object = datetime.datetime.strptime(d2, '%Y-%m-%d %H:%M:%S')
            date = datetime_object.strftime("%Y-%m-%d %H:%M")
        except:
            print('     Could not find LIVEJOURNAL publish date.', file = log)
    elif 'wordpress' in url:
        #In Wordpress the blog layouts vary too much :( 
        print('     Could not find WORDPRESS publish date.', file = log)
    else:
        print('     Could not find publish date!', file = log)
    print('     Publishing time stamp: ' + date, file = log)
    return date


#Collecting links
def links(page_content, baselink, log):
    collected_links = set()
    try:
        Atags = page_content.find_all('a', href=True)
        if Atags == 0:
            print('     Could not find any outgoing links.', file = log)
            pass
        else:
            for link in Atags:
                if 'http' in link['href']:
                    collected_links.add(link['href'])
                else:
                    #if internal links then create full urls
                    joinedlink = urljoin(baselink, link['href'])
                    collected_links.add(joinedlink)
    except:
        print('     Could not find any outgoing links.', file = log)
    #check if link has been collected before
    links_so_far = list(collected_links)
    for link in links_so_far:
        for item in sg.seen_already:
            if link == item:
                collected_links.discard(link)
                break
    #IN CASE you want to write new links to a file
    '''with codecs.open('links_out.txt', 'a', encoding='utf-8') as f:
        for link in collected_links:
            f.write(link+'\r\n')'''
    print('     Number of new links: ' + str(len(collected_links)), file = log)
    return collected_links



#Collecting text
def text(page_content, log):
    p_contents = []
    for i in page_content.find_all('p'):
        p_contents.append(i.text)
    fulltext = ' '
    fulltext = fulltext.join(p_contents)
    fulltext = fulltext.replace('"', '?')
    print('     Number of characters in collected text: ' + str(len(fulltext)), file = log)
    return fulltext



#Collecting author
def author(url, log):
    author = 'unknown'
    if 'bookz.ru/authors/' in url:
        spliturl = url.split('/')
        author = str(spliturl[4])
    print('     Author: ' + author, file = log)
    return author



#Collecting comments (works only with some pages)
def collect_comments(page_content, url, log):
    comments_dict = {}
    x = 0
    if 'ari.ru' in url:
        try:
            for i in page_content.find_all('li', id=True):
                x += 1
                comment_num = 'Comment_' + str(x)
                comment = {}
                comment['vk_user_id'] = i.div.cite.a['href']
                comment['vk_user_name'] = i.div.cite.a.string
                comment['vk_user_comment'] = ''
                for sibling in i.find_all('div', class_='cackle-comment-message'):
                    comment['vk_user_comment'] = sibling.string
                comments_dict[comment_num] = comment
        except:
            print('     Error with collecting comments or no comments found.', file = log)
    elif 'pandoraopen.ru' in url:
        try:
            author_tags = page_content.find_all('a', class_='athr')
            date_tags = page_content.find_all('a', class_='dt')
            comment_tags = page_content.find_all('div', class_='t')
            comments_dict = {}
            x = 0
            for i in author_tags:
                x += 1
                comment_num = 'Comment_' + str(x)
                comment = {}
                comment['c_user_id'] = i['href']
                comment['c_user_name'] = author_tags[x-1].string
                d = date_tags[x-1].string
                rusm, numm = sm.month_conversion(d)
                d2 = d.replace(str(rusm), str(numm))
                datetime_object = datetime.datetime.strptime(d2, '%d %m %Y в %H:%M')
                date = datetime_object.strftime("%Y-%m-%d %H:%M")
                comment['c_comment_date'] = date
                c = ''
                for p in comment_tags[x-1].children:
                    c = c + str(p)
                comment['c_user_comment'] = c
                comments_dict[comment_num] = comment
        except:
            print('     Error with collecting comments or no comments found.', file = log)
    print('     Number of collected comments: ' + str(x), file = log)
    return comments_dict, x




#Dictionary
def makeDict(language, level, prefix, file_num, url, scrape_date, date, author, collected_links, text_content):
    data = OrderedDict([
        ("doc_id", (language+'_'+level+'_'+prefix+'_'+str(file_num))),
        ("url", url),
        ("scrape_date", scrape_date),
        ("publish_date", date),
        ("author", author),
        ("urls_out", collected_links),
        ("text", text_content)
        ])
    return data


#Writing to file 
def makeFile(filename, data, log, savepath):
    directory_path = savepath + '/' + filename
    try:
        with codecs.open(directory_path, 'w', encoding='utf-8') as fp:
            json.dump(data, fp, ensure_ascii=False, sort_keys=False, indent=4)
        print('     File was created.', file = log)
    except:
        print('     Error when writing the JSON-file.\r\n', file = log)




