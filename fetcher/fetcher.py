#!/usr/bin/env python3.7
#
# author:  Karl McGuire (karl@karlmcguire.com)
# license: MIT

"""Fetches UNCC police log files and saves them to disk.

This script scrapes the list of log files at https://police.uncc.edu/police-log
and writes each log PDF to disk with their respective dates as filenames.
"""

import os
from requests import get
from bs4 import BeautifulSoup as soup

# directory specifies the local directory to store the log files - if it doesn't
# already exist it will be created
directory = "./pdfs/"

# head contains the user-agent http header so the IT guys can't distinguish our
# scraping traffic from normal browser traffic (and ruin our fun)
head = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.3"
                    "6 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36")
}

# pref is the url prefix used for getting both the list of log files and the log
# files themselves
pref = "https://police.uncc.edu/"

# resp contains the http response with the raw html of the log list page
resp = get(pref + "police-log", headers=head)

# logs will contain the url suffixes for each log file listed
logs = []

# for each <a> tag on the log list page check if it's a link containing a full
# path to a log file and if so: add it to the logs list
for link in soup(resp.text, "html.parser").find_all("a"):
    # make sure there's actually a href for the <a> tag (yes, believe it or not
    # there are <a> tags on the page without hrefs)
    if "href" in link.attrs.keys():
        href = link["href"]
        # the police log files contain "police.uncc.edu" in their href (for now)
        if link["href"].find("police.uncc.edu") != -1:
            # add the url suffix to the log list
            logs.append(link["href"])

try:
    # create pdfs/ directory
    os.mkdir(directory)
except FileExistsError:
    # doesn't matter if the directory already exists
    pass

# for each log listed on the page, download the pdf file and write the contents
# to disk under the pdfs/ folder
#
# note: we're iterating in reversed order because some logs get revised and
# therefore listed twice under the same date, iterating in reverse order allows
# us to overwrite the previously written log file with the revised version
for log in reversed(logs):
    # year contains the index of the year number in the log filename
    year = log.find("2019")
    # date is the mm-dd-yyyy date of the log file, to be used as the filename
    # for the log pdf on disk
    date = log[year - 6 : year + 4]
    # name is the local filename of the log pdf
    name = date + ".pdf"

    # data contains the http response with the raw pdf data of the current log
    data = get(pref + log, headers=head, stream=True)

    # write the pdf to disk under pdfs/ directory
    with open(directory + name, "wb") as file:
        for chunk in data.iter_content(chunk_size=128):
            file.write(chunk)

    # this loop may take a while, keep the user updated
    print("done: " + directory + name)
