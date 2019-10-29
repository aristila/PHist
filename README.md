<h1>PHist</h1>
A web scraper in Python3 that utilizes BeautifulSoup and writes the results into JSON format. 

This program was created for Pseudohistoria project at the University of Turku (https://sites.utu.fi/pseudohistoria/en/). The program was coded by Anna Ristilä and contributed to by Mila Oiva, who helped with the processing of Russian materials. 


<h2>Required modules</h2>
The program uses the following extra modules:
<ul>
	<li>beatufulsoup4 (https://pypi.org/project/beautifulsoup4/)</li>
	<li>robotexclusionrulesparser (https://pypi.org/project/robotexclusionrulesparser/)</li>
</ul>

<h2>Usage</h2>
The program was designed to be run from command line with some arguments: 
<ul>
	<li> -s name_of_seedfile</li>
	<li> -p prefix_tag</li>
	<li> -l language_tag</li>
	<li> -L level_tag</li>
</ul>
The seed file should be in plain text and contain one link on one line. Currently, the code only understands Windows newlines "\r\n". 

The other arguments are for distinguishing files and are used in filenames. The prefix and level tags are also used as names of subdirectories. 

Running the scraper_bs4_MAIN.py with valid arguments and a list of seed links will produce as many JSON files as the scraper is able to scrape from the seed file list without problems. The program will keep a log file which is constantly updated, so if something goes wrong and the program crashes or hangs, you can go see which seed link caused the problem. Links ending with .mp3 or other media format are currently a problem. 

The program also keeps track of all the processed links, but writes them into files only at the end of the cycle. The program does not scrape social media links but records them for possible future use. 

The files created py the program:
<ul>
	<li> JSON files</li>
	<li> outgoing links for next scrape cycle</li>
	<li> facebook links</li>
	<li> twitter links</li>
	<li> vkontakte links</li>
	<li> linkedin links</li>
	<li> all scraped links</li>
	<li> links not found</li>
	<li> links disallowed by robots.txt</li>
	<li> links whose robots.txt file could not be found</li>
</ul>
