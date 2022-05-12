from pyzotero import zotero
from scholarly import scholarly

import numpy as np
import os.path

import io
import requests
import json
from PyPDF2 import PdfFileReader

from urllib.request import urlopen, Request
from bs4 import BeautifulSoup

def save_all_data(papers, fname):
    """
    Saves a list of papers to storage (json file)
    :param papers: list of paper dictionaries
    :type papers: `list`
    :param fname: file name
    :type fname: `str`
    """
    if os.path.isfile(fname):
        # if the file already exists, just append to it
        with open(fname, 'r+') as file:
            # First we load existing data into a dict.
            file_data = json.load(file)
            # Join new_data with file_data inside emp_details
            for paper in papers:
                file_data['papers'][paper['data']['title']] = paper
            # Sets file's current position at offset.
            file.seek(0)
            # convert back to json.
            json.dump(file_data, file, indent=4)
    else:
        dict = {'papers': {}}
        for paper in papers:
            dict['papers'][paper['data']['title']] = paper
        with open(fname, 'w') as fp:
            json.dump(dict, fp)


def add_title_to_zotero(titles, zotero_id, zotero_library, zotero_key):
    """
    Add a list of papers (titles provided) to Zotero library.
    :param titles: list of titles to add
    :type titles: `list`
    """
    zot = zotero.Zotero(zotero_id, zotero_library, zotero_key)
    for title in titles:
        template = zot.item_template('journalArticle')
        template['title'] = title
        resp = zot.create_items([template])
        if resp['failed'] == {}:
            print('Successfully added', title, 'to Zotero')
        else:
            print('Failed to add', title, 'to Zotero')


def get_related_papers(titles, related=True, cited_by=False):
    """
    Finds papers that, according to google scholar, are related to and/or cited by the provided paper titles.
    :param titles: the titles of the papers from which to find related papers and/or cited by papers
    :type titles: `list`
    :param related: if True, the related papers will be sought
    :type related: `bool`
    :param cited_by: if True, the cited by papers will be sought
    :type cited_by: `bool`
    :return: list of related paper title strings
    :rtype: `list`
    """
    related_papers = []
    for title in titles:
        # find title through google scholar
        search_query = scholarly.search_pubs(title)
        # uses the first result
        paper = next(search_query)
        if related:
            related_url = 'https://scholar.google.com' + paper['url_related_articles']
            related_papers = related_papers + title_from_scholar_search_result(related_url)
        if cited_by:
            cited_by_url = 'https://scholar.google.com' + paper['citedby_url']
            related_papers = related_papers + title_from_scholar_search_result(cited_by_url)
    return related_papers


def title_from_scholar_search_result(url):
    """
    Scrapes a Google Scholar search result and extracts the paper titles
    :param url: url corresponding to the Google Scholar results
    :type url: `str`
    :return: list of title strings
    :rtype: `list`
    """
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urlopen(req).read()
    soup = BeautifulSoup(html, features="html.parser")
    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()  # rip it out
    # get text
    text = soup.get_text()
    split = text.split('[PDF]')[1:]
    titles = []
    for s in split:
        if '[HTML]' in s:
            split2 = s.split('[HTML]')
            s1 = split2[3]
            # this assumes more than one author (separated by commas)
            # todo: handle the one author case
            end_ind = find_end_of_title(s1, 1)
            titles.append(s1[1:end_ind])
        # finding the end of the publication link (.com, .org, etc.)
        start_ind = s.find('.') + 4
        end_ind = find_end_of_title(s, start_ind)
        titles.append(s[start_ind:end_ind])
    return titles


def find_end_of_title(s, start_ind):
    """
    Helper function for extracting titles (specifically, finding the end of one)
    from scraping a Google Scholar search result
    :param s: substring that the title is in and that the end index needs to be found from
    :type s: `str`
    :param start_ind: index of the first character if the title within the provided string
    :type start_ind: `int`
    :return: index of the last character of the title within the initial provided string
    :rtype: `int`
    """
    end_ind = s.find(',') - 1
    if end_ind != -2:
        found = False
        while (end_ind > 0) and not found:
            if s[end_ind] == ' ':
                found = True
            end_ind = end_ind - 1
    else:
        end_ind = start_ind + 30
    return end_ind


def paper_data_from_zotero(zotero_id, zotero_library, zotero_key, n=-1):
    """
    Retrieves paper dictionaries from Zotero
    :param n: max number of papers to retrieve (retrieve all if n = -1)
    :type n: `int`
    :return: list of paper dictionaries taken from Zotero library
    :rtype: `list`
    """
    zot = zotero.Zotero(zotero_id, zotero_library, zotero_key)
    if n == -1:
        items = zot.top()
    else:
        items = zot.top(limit=n)
    return items


def dictionary_from_google_scholar(title):
    """
    Gets paper info from Google Scholar and puts it into a dictionary that matches the form Zotero uses
    :param title: title of paper to search Google Scholar with
    :type title: `str`
    :return: dictionary of paper info in the form that Zotero uses
    :rtype: `dict`
    """
    paper = {}
    # find title through google scholar
    search_query = scholarly.search_pubs(title)
    # uses the first result
    result = next(search_query)
    # save relevant information in a dictionary in the form that zotero uses
    paper['data']['title'] = title
    # try to extract the abstract from the pub page
    paper['data']['abstractNote'] = abstract_from_pub_page(result['pub_url'])
    if paper['data']['abstractNote'] is '':
        # try to find the abstract from the full text if it could not be found from the pub page
        paper['data']['abstractNote'] = abstract_from_pdf(result['eprint_url'])
    paper['data']['url'] = result['eprint_url']
    return paper


def text_from_paper_dict(paper, abstract=True):
    """
    Gets text (full text or abstract) for a provided paper dictionary (from Zotero).
    If the desired text cannot be found through Zotero data, attempts to find through Google Scholar.
    :param paper: Paper data from Zotero
    :type paper: `dict`
    :return: desired paper text
    :rtype: `str`
    """
    if abstract:
        if paper['data']['abstractNote'] is not '':
            return paper['data']['abstractNote']
        elif paper['data']['url'] is not '':
            # try to find from a url
            if '.pdf' == paper['data']['url'][-4:]:
                return abstract_from_pdf(paper['data']['url'])
            else:
                return abstract_from_pub_page(paper['data']['url'])
        else:
            # try to find from google scholar
            return text_from_google_scholar(paper['data']['title'], True)
    else:
        if (paper['data']['url'] is not '') and ('.pdf' == paper['data']['url'][-4:]):
            return full_text_from_pdf(paper['data']['url'])
        else:
            # try to find from google scholar
            return text_from_google_scholar(paper['data']['title'], False)


def text_from_google_scholar(title, abstract=True):
    """
    Gets desired text for provided paper title from Google Scholar
    :param title: Paper title to search Google Scholar with
    :type title: `str`
    :param abstract: True if the abstract is desired, False if full text is desired
    :type abstract: `bool`
    :return: desired text
    :rtype: `str`
    """
    # find title through google scholar
    search_query = scholarly.search_pubs(title)
    # uses the first result
    try:
        paper = next(search_query)
    except:
        print('Could not find', title, 'through Google Scholar')
    else:
        if abstract:
            if (paper['pub_url'] is not ''):
                return abstract_from_pub_page(paper['pub_url'])
            elif (paper['eprint_url'] is not ''):
                return abstract_from_pdf(paper['pub_url'])
        else:
            return full_text_from_pdf(paper['eprint_url'])


def full_text_from_pdf(pdf):
    """
    Gets full paper text from a provided paper pdf url.
    Will not get the abstract.
    :param pdf: url for the full paper text pdf
    :type pdf: `str`
    :return: full paper text
    :rtype: `str`
    """
    text = ''
    if '.pdf' == pdf[-4:]:
        r = requests.get(pdf)
        f = io.BytesIO(r.content)
        reader = PdfFileReader(f)
        n_pages = reader.getNumPages()
        for p in range(n_pages):
            text += reader.getPage(p).extractText()
    else:
        print('ERROR: provided url is not a paper pdf')


def abstract_from_pdf(pdf):
    """
    Gets abstract from a provided paper publication url.
    Will not get the full text.
    :param pdf: url for the full paper text pdf
    :type pdf: `str`
    :return: abstract text
    :rtype: `str`
    """
    text = ''
    r = requests.get(pdf)
    f = io.BytesIO(r.content)
    reader = PdfFileReader(f)
    n_pages = reader.getNumPages()
    for p in range(n_pages):
        text += reader.getPage(p).extractText()
    abstract = extract_abstract(text)
    return abstract


def abstract_from_pub_page(url):
    """
    Gets abstract from a provided paper publication url.
    Will not get the full text.
    :param url: publication url
    :type url: `str`
    :return: abstract text
    :rtype: `str`
    """
    html = urlopen(url).read()
    soup = BeautifulSoup(html, features="html.parser")
    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()  # rip it out
    # get text
    text = soup.get_text()
    abstract = extract_abstract(text)
    return abstract


def extract_abstract(text):
    """
    Attempts to extract only the abstract from a paper's publication page text
    :param text: text, which should include abstract
    :type text: `str`
    :return: abstract text
    :rtype: `str`
    """
    # break into lines and remove leading and trailing space on each
    lines = [line.strip() for line in text.splitlines()]
    extract = False
    found = False
    abstract = ''
    i = 0
    n_lines = len(lines)
    while not found and i < n_lines:
        line = lines[i]
        if (line == '' or 'Introduction' in line) and extract:
            found = True
        elif extract:
            abstract += line
        elif 'abstract' in line.lower():
            # if the next line doesn't have a space in it (is not a sentence), then this was probably just
            # a random tag/link
            if ' ' in lines[i+1]:
                abstract += line
                extract = True
        i += 1
    abstract = abstract.replace('Abstract', '')
    return abstract
