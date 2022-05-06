from pyzotero import zotero
from scholarly import scholarly

import numpy as np
import os.path

import io
import requests
#from pyPdf import PdfFileReader
from PyPDF2 import PdfFileReader

from urllib.request import urlopen
from bs4 import BeautifulSoup

import pdb

# personal library ID
ID = 8601934
LIBRARY = 'user'
APIKEY = 'CzACnmlnHkQxIbkjj1y2tNzu'

def save_to_npz(papers, fname):
    """
    Saves a list of papers to storage (currently npz file)
    :param papers: list of paper triples [(ID1, Title1, Abstract1), (ID2, Title2, Abstract2), ...]
    :type papers: `list`
    :param fname: file name
    :type fname: `str`
    """
    # save list of paper IDs, title, and abstract triples to npz file
    to_save = np.array(papers)
    # if the file already exists, read from it, append to it, then resave
    if os.path.isfile(fname):
        old = np.load(fname)
        # todo: maybe ensure we're not adding duplicates, which could be expensive (searching)
        to_save = np.concatenate([old, to_save])
    np.savez_compressed(fname, to_save)
    print('Saved successfully to file', fname)

def dicts_from_zotero(n=-1):
    """
    Retrieves paper dictionaries from Zotero
    :param n: max number of papers to retrieve (retrieve all if n = -1)
    :type n: `int`
    :return: list of paper dictionaries taken from Zotero library
    :rtype: `list`
    """
    zot = zotero.Zotero(ID, LIBRARY, APIKEY)
    if n == -1:
        items = zot.top()
    else:
        items = zot.top(limit=n)
    """ dictionary keys: 'key', 'version', 'itemType', 'title', 'creators', 'abstractNote',
    'publicationTitle', 'volume', 'issue', 'pages', 'date', 'series', 'seriesTitle', 'seriesText',
    'journalAbbreviation', 'language', 'DOI', 'ISSN', 'shortTitle', 'url', 'accessDate', 'archive',
    'archiveLocation', 'libraryCatalog', 'callNumber', 'rights', 'extra', 'tags', 'collections', 'relations',
    'dateAdded', 'dateModified' """
    return items

def dict_to_list(papers):
    """
    Zotero stores paper data in a dictionary.
    This function converts it to a list that's useful for storage.
    :param papers: list of paper dictionaries
    :type papers: `list`
    :return: list of paper triples [(ID1, Title1, Abstract1), (ID2, Title2, Abstract2), ...]
    :rtype: `list`
    """
    ret_lst = []
    for item in papers:
        ret_lst.append((item['data']['key'], item['data']['title'], item['data']['abstractNote']))
    return ret_lst

def text_from_pdf(pdf):
    """
    Gets full paper text from a provided paper pdf url.
    Will not the the abstract.
    :param url: url for the full paper text pdf
    :type url: `str`
    :return: full paper text
    :rtype: `str`
    """
    text = ''
    if '.pdf' == pdf[-4:]:
        # get text from a pdf
        r = requests.get(pdf)
        f = io.BytesIO(r.content)
        reader = PdfFileReader(f)
        n_pages = reader.getNumPages()
        for p in range(n_pages):
            text += reader.getPage(p).extractText()
    else:
        print('ERROR: provided url is not a paper pdf')

def abstract_from_url(url, abstract_only=True):
    """
    Gets abstract from a provided paper publication url.
    Will not get the full text.
    :param url: publication url
    :type url: `str`
    :param abstract_only: True if only the actual abstract text is desired, False if the full page text is desired
    :type abstract_only: `bool`
    :return: abstract text
    :rtype: `str`
    """
    if '.pdf' == url[-4:]:
        print('WARNING: provided a pdf, which might be a full paper, therefore, the abstract may not be able to be '
              'extracted')
    html = urlopen(url).read()
    soup = BeautifulSoup(html, features="html.parser")
    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()  # rip it out
    # get text
    text = soup.get_text()
    # break into lines and remove leading and trailing space on each
    lines = [line.strip() for line in text.splitlines()]
    if abstract_only:
        text = extract_abstract(lines)
    else:
        text = full_pub_page_text(lines)
    return text

def extract_abstract(lines):
    """
    Attempts to extract only the abstract from a paper's publication page text
    :param lines: list of lines from a publication page
    :type lines: `list`
    :return: abstract text
    :rtype: `str`
    """
    extract = False
    found = False
    text = ''
    i = 0
    n_lines = len(lines)
    while not found and i < n_lines:
        line = lines[i]
        if line == '' and extract:
            found = True
        elif extract:
            text += line
        elif 'abstract:' in line.lower():
            text += line
            extract = True
        i += 1
    return text

def full_pub_page_text(lines):
    """
    Cleans all provided text (from a paper's publication page)
    :param lines: list of lines from a publication page
    :type lines: `list`
    :return: cleaned full page text
    :rtype: `str`
    """
    # break multi-headlines into a line each
    chunks = [phrase.strip() for line in lines for phrase in line.split("  ")]
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text

def full_text_from_paper_dict(paper, abstract=True):
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
        else:
            # try to find from google scholar
            return text_from_google_scholar(paper['data']['title'], True)
    else:
        if paper['data']['url'] is not '':
            return text_from_pdf(paper['data']['url'])
        else:
            # try to find from google scholar
            return text_from_google_scholar(paper['data']['title'], False)

def text_from_google_scholar(title, abstract=True):
    """
    Gets for provided paper title from Google Scholar
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
    paper1 = next(search_query)
    """ dictionary keys: 'container_type', 'source', 'bib', 'filled', 'gsrank', 'pub_url'
    'author_id', 'url_scholarbib', 'url_add_sclib', 'num_citations'
    'citedby_url', 'url_related_articles', 'eprint_url'"""
    if abstract:
        if paper1['pub_url'] is not '':
            text = abstract_from_url(paper1['pub_url'])
    else:
        text = text_from_pdf(paper1['eprint_url'])
    return text

# Get the first paper from my library (Attack-Resistant Federated Learning with Residual-based Reweighting))
papers = dicts_from_zotero()
paper1 = papers[0]
# Finds the paper's abstract from the publication link in Zotero and prints it
abstract1 = abstract_from_url(paper1['data']['url'])
print(abstract1)
