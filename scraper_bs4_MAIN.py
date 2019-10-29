#PHist 1.1 web scraper
#Scrapes sites with BeautifulSoup4
#MAIN PROGRAM

import codecs, requests, json, datetime, time, os
import sys, getopt
import robotexclusionrulesparser
from urllib.parse import urljoin
import scraper_module as sm
import scraper_globals as sg
from bs4 import BeautifulSoup
from collections import OrderedDict



#___SETUP:___

#SEEDFILE and PREFIX
'''
Give the seedfile name as a command line argument:
[script name] [-s] [seed file name] 
This file should be in plain text format (.TXT with encoding = utf-8).
DO NOT USE Microsoft Word documents or equivalent, because
they usually include some metadata that screws things up.
File for testing: test_seedlink.txt
File for the real deal: fin_data_seedlinks.txt
File for full level 2 scrape list: FIN_L2_links.txt

Optional:
Give a filename prefix as a command line argument:
[script name] [-p] [prefix name]
Prefix is used to track files for each partial cycle.
Default prefix is empty.
'''

#Reads commandline arguments
fullCmdArguments = sys.argv
argumentList = fullCmdArguments[1:]

#Defines valid parameters
unixOptions = "hs:l:L:p:"
gnuOptions = ["help", "seedfile=", "language=", "level=", "prefix="]

#Parses the argument list
try:
    arguments, values = getopt.getopt(argumentList, unixOptions, gnuOptions)
except getopt.error as err:
    # output error, and return with an error code
    print (str(err))
    sys.exit(2)

#Goes through arguments and takes actions accordingly
for currentArgument, currentValue in arguments:
    if currentArgument in ("-h", "--help"):
        print ('''Syntax:
     [script name] [-s] [seed file name]
	 [script name] [-l] [language tag, e.g. FIN or RUS]
	 [script name] [-L] [scrape level tag: SEED, L2 or L3]
     [script name] [-p] [optional prefix tag]''')
    elif currentArgument in ("-s", "--seedfile"):
        print (("Seedfile to be used is (%s)") % (currentValue))
        sg.seedfile = currentValue
    elif currentArgument in ("-l", "--language"):
        print (("Language of scraped files is (%s)") % (currentValue))
        sg.language = currentValue
    elif currentArgument in ("-L", "--level"):
        print (("Scrape level is (%s)") % (currentValue))
        sg.level = currentValue
    elif currentArgument in ("-p", "--prefix"):
        print (("Prefix for output files is (%s)") % (currentValue))
        sg.prefix = currentValue


#Creates time stamp for files
now = datetime.datetime.now()
t = now.strftime("%Y-%m-%d-%H%M%S")

#Make directories if needed

##Current working directory
cwd = os.getcwd()
print(cwd)

##Sets access rights for the directories
accessrights = 0o755	# 755 = readable by all, writeable by owner only
						# 777 = readable and writeable by all

##Creates the required directories and defines where the files will be saved
resultpath = cwd + '/results'
resultpath2 = resultpath + '/' + sg.level
prefixpath = ''
savepath = resultpath2
if not os.path.exists(resultpath):
    try:
        os.mkdir(resultpath, accessrights)
    except:
        print('Creation of the directory %s failed' % resultpath)
    else: 
        print('Successfully created the path %s' % resultpath)
if not os.path.exists(resultpath2):
    try:
        os.mkdir(resultpath2, accessrights)
    except:
        print('Creation of the directory %s failed' % resultpath2)
    else: 
        print('Successfully created the path %s' % resultpath2)
if sg.prefix != '':	#if a prefix was given, creates a subdirectory for it and saves there
    prefixpath = resultpath2 + '/' + sg.prefix
    if not os.path.exists(prefixpath):
        try:
            os.mkdir(prefixpath, accessrights)
        except:
            print('Creation of the directory %s failed' % prefixpath)
        else: 
            print('Successfully created the path %s' % prefixpath)
    savepath = prefixpath


#Log file name
logf = savepath + '/' + sg.language + '_' + sg.level + '_' + sg.prefix + '_' + t + '_LOG.txt'
print('The log file will be named ' + logf)



#Cycle for handling all links
def cycle(level, links_to_be_scraped, link_repository, log):
    
    print('Iterating ' + level + ' level links...', file = log)
    log.flush()
    iter_num = 0

    for link in links_to_be_scraped:

        print('\r\nURL: ' + str(link), file = log)
        log.flush()
        
        #Checks if link has already been processed before
        if sm.check_seen(link) == True:
            print('     Seen this link before - did not scrape.', file = log)
            log.flush()
            continue
                
        #Discards YouTube links
        if 'youtube.com' in link:
            print('     YouTube link found - did not scrape.', file = log)
            log.flush()
            continue

        #Discards mailto: links
        if 'mailto:' in link:
            print('     Mailto link found - did not scrape.', file = log)
            log.flush()
            continue

        #Collects Facebook links for future use but does not scrape
        if 'facebook.com' in link:
            print('     Facebook link found - stored but did not scrape.', file = log)
            log.flush()
            sg.facebook_links.append(link)

        #CollectsF Twitter links for future use but does not scrape
        if 'twitter.com' in link:
            print('     Twitter link found - stored but did not scrape.', file = log)
            log.flush()
            sg.twitter_links.append(link)

        #Collects VK links for future use but does not scrape
        if 'vk.com' in link:
            print('     VK link found - stored but did not scrape.', file = log)
            log.flush()
            sg.vk_links.append(link)

        #Collects Linkedin links for future use but does not scrape
        if 'linkedin.com' in link:
            print('     Linkedin link found - stored but did not scrape.', file = log)
            log.flush()
            sg.linkedin_links.append(link)

        #Checks ROBOTS.TXT; if not allowed to scrape, moves to next link
        print('     Checking robots.txt...', file=log)
        log.flush()
        answer, err = sm.checkRobotstxt(link)
        if err == (True):
            print('     Problem with reading ROBOTS.TXT - did not scrape.', file = log)
            log.flush()
            sg.robotstxt_not_found.append(link)
            continue
        elif err == False and answer == (False):
            print('     The website does not allow the scraping of this link.', file = log)
            log.flush()
            sg.disallowed.append(link)
            sg.seen_already.add(link)
            continue
        else:
            print('     Scraping allowed!', file = log)
            log.flush()


        #Collects page contents; if no content found, moves to next link
        page_content = sm.soup(link, log)
        print('     Got page contents!', file = log)
        log.flush()        
        if page_content == 0:
            print('     Something went wrong or no page content found.', file = log)
            sg.not_found.append(link)
            sg.seen_already.add(link)
            continue
        elif page_content == 1:
            print('     Connection error / no page content found.', file = log)
            sg.not_found.append(link)
            sg.seen_already.add(link)
            continue
        else:                
            #Keeps track of file
            iter_num += 1
            file_num = sm.numFile(iter_num)
            full_filename = sg.language + '_' + sg.level + '_' + sg.prefix + '_' + t + '_' + str(file_num) + '.json'
            print('File number: ' + sg.prefix + '_' + file_num)
            print('File number: ' + sg.prefix + '_' + file_num, file = log)
            
            #Records data
            url = str(link)                                 #records current url
            a = sm.scr_date(log)                            #records current date and time
            b = sm.pub_date(page_content, link, log)        #records text publish date
            c = sm.author(url, log)                         #records author
            d = list(sm.links(page_content, link, log))     #records new found links as a list (modify sm.links to write collected links into a separate file 'links_out.txt')
            e = sm.text(page_content, log)                  #records all text inside p-tags as one string

            f, num_of_comments = sm.collect_comments(page_content, link, log)     #records comments as a dictionary and the number of comments

            #Adds url to scraped list and seen list
            sg.scraped_links.append(url)
            sg.seen_already.add(url)

            #Adds collected links to the next level link repository
            for link in d:
                link_repository.add(link)
            
            #creates a dictionary of all the collected data except comments
            x = sm.makeDict(sg.language, sg.level, sg.prefix, file_num, url, a, b, c, d, e)      

            #creates a JSON file of all collected data except comments
            sm.makeFile(full_filename, x, log, savepath)                 

            #If comments were found, creates a separate file for comments
            if num_of_comments > 0:
                comments_filename = full_filename + '_comments.json'
                sm.makeFile(comments_filename, f, log)

            #Flushes the log file
            log.flush()
            
            #suspend execution for one second
            time.sleep(1)


#___MAIN_CODE___

print('Starting...')

#Starting time
start_time = time.time()

#Gets the seed links and cycles through them
log = open(logf, 'a', encoding='utf-8')
print('Opened log file...')
print('Getting seed links...', file = log)
log.flush()
seed_links = sm.get_seeds(sg.seedfile)
print('Got seed links!', file = log)
log.flush()
cycle(sg.level, seed_links, sg.links_L2, log)
log.close()

#Writes stats to files
outfile = savepath + '/' + sg.language + '_' + sg.level + '_' + sg.prefix + '_' + t + '_outgoing_links_for_next_srape_cycle.txt'
fb_file = savepath + '/' + sg.language + '_' + sg.level + '_' + sg.prefix + '_' + t + '_facebook_links.txt'
tw_file = savepath + '/' + sg.language + '_' + sg.level + '_' + sg.prefix + '_' + t + '_twitter_links.txt'
vk_file = savepath + '/' + sg.language + '_' + sg.level + '_' + sg.prefix + '_' + t + '_vkontakte_links.txt'
li_file = savepath + '/' + sg.language + '_' + sg.level + '_' + sg.prefix + '_' + t + '_linkedin_links.txt'
sc_file = savepath + '/' + sg.language + '_' + sg.level + '_' + sg.prefix + '_' + t + '_scraped_links.txt'
nf_file = savepath + '/' + sg.language + '_' + sg.level + '_' + sg.prefix + '_' + t + '_not_found_links.txt'
da_file = savepath + '/' + sg.language + '_' + sg.level + '_' + sg.prefix + '_' + t + '_disallowed_links.txt'
rp_file = savepath + '/' + sg.language + '_' + sg.level + '_' + sg.prefix + '_' + t + '_robotstxt_not_found_links.txt'

with open(outfile, 'w', encoding='utf-8', errors='replace') as of:
    for i in sg.links_L2:
        of.write(i+'\r\n')
with open(fb_file, 'w', encoding='utf-8', errors='replace') as fbf:
    for i in sg.facebook_links:
        fbf.write(i+'\r\n')
with open(tw_file, 'w', encoding='utf-8', errors='replace') as twf:
    for i in sg.twitter_links:
        twf.write(i+'\r\n')
with open(vk_file, 'w', encoding='utf-8', errors='replace') as vkf:
    for i in sg.vk_links:
        vkf.write(i+'\r\n')
with open(li_file, 'w', encoding='utf-8', errors='replace') as lif:
    for i in sg.linkedin_links:
        lif.write(i+'\r\n')
with open(sc_file, 'w', encoding='utf-8', errors='replace') as scf:
    for i in sg.scraped_links:
        scf.write(i+'\r\n')
with open(nf_file, 'w', encoding='utf-8', errors='replace') as nff:
    for i in sg.not_found:
        nff.write(i+'\r\n')
with open(da_file, 'w', encoding='utf-8', errors='replace') as daf:
    for i in sg.disallowed:
        daf.write(i+'\r\n')
with open(rp_file, 'w', encoding='utf-8', errors='replace') as rpf:
    for i in sg.robotstxt_not_found:
        rpf.write(i+'\r\n')


with open(logf, 'a', encoding='utf-8') as log:
    #Prints out final stats
    print('*'*30, file = log)
    print('Scraped ' + str(len(sg.scraped_links)) + ' urls.', file = log)
    print('Could not scrape ' + str(len(sg.not_found)+len(sg.disallowed)) + ' urls.', file = log)
    print(str(len(sg.seen_already)) + ' unique links processed.', file = log)

    #Prints out elapsed time
    elapsed_time = time.time() - start_time
    showtime = str(datetime.timedelta(seconds=elapsed_time))
    print('Time it took to execute this program: ' + str(showtime), file = log)


print('\r\nDone!')
