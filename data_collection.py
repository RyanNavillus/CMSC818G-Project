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

import pdb


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


def get_related_papers(titles, related=True, cited_by=True):
    """
    Finds papers that, according to google scholar, are related to and/or cited by the provided paper titles.
    :param titles:
    :type titles: `list`
    :param related:
    :type related: `list`
    :param cited_by:
    :type cited_by: `list`
    :return:
    :rtype: `list`
    """
    related_papers = []
    for title in titles:
        print(title)
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

    :param url:
    :type url: `list`
    :return:
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

    :param s:
    :type s: `list`
    :param start_ind:
    :type start_ind: `list`
    :return:
    :rtype: `list`
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
    """ dictionary keys: 'key', 'version', 'itemType', 'title', 'creators', 'abstractNote',
    'publicationTitle', 'volume', 'issue', 'pages', 'date', 'series', 'seriesTitle', 'seriesText',
    'journalAbbreviation', 'language', 'DOI', 'ISSN', 'shortTitle', 'url', 'accessDate', 'archive',
    'archiveLocation', 'libraryCatalog', 'callNumber', 'rights', 'extra', 'tags', 'collections', 'relations',
    'dateAdded', 'dateModified' """
    return items


def dictionary_from_google_scholar(title):
    """

    :param title:
    :type title:
    :return:
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


"""
['Google ScholarLoading...The system can\'t perform the operation now. Try again later.CiteAdvanced searchFind articleswith all of the wordswith the exact phrasewith at least one of the wordswithout the wordswhere my words occuranywhere in the articlein the title of the articleReturn articles authored bye.g., "PJ Hayes" or McCarthyReturn articles published ine.g., J Biol Chem or NatureReturn articles dated between\xa0—\xa0e.g., 1996Saved to My libraryDoneRemove articleArticlesCase lawProfilesMy profileMy libraryAlertsMetricsAdvanced searchSettingsSign inSign inArticlesScholar1 result (0.01 sec)My profileMy libraryYearAny timeSince 2022Since 2021Since 2018Sort by relevanceSort by dateAny timeSince 2022Since 2021Since 2018Custom range... — SearchSort by relevanceSort by dateCreate alertCertifiably-Robust Federated Adversarial Learning via Randomized SmoothingSearch within citing articles 
[PDF] arxiv.orgSoK: On the Security & Privacy in Federated LearningG Abad, S Picek, A Urbieta\xa0- arXiv preprint arXiv:2112.05423, 2021 - arxiv.orgAdvances in Machine Learning (ML) and its wide range of applications boosted its popularity. Recent privacy awareness initiatives as the EU General Data Protection\xa0…Save Cite Related articles All 2 versions  View as HTML Create alertHelpPrivacyTerms']

['Google ScholarLoading...The system can\'t perform the operation now. Try again later.CiteAdvanced searchFind articleswith all of the wordswith the exact phrasewith at least one of the wordswithout the wordswhere my words occuranywhere in the articlein the title of the articleReturn articles authored bye.g., "PJ Hayes" or McCarthyReturn articles published ine.g., J Biol Chem or NatureReturn articles dated between\xa0—\xa0e.g., 1996Saved to My libraryDoneRemove articleArticlesCase lawProfilesMy profileMy libraryAlertsMetricsAdvanced searchSettingsSign inSign inArticlesScholarAbout 101 results (0.02 sec)My profileMy libraryRelated articles 
[PDF] arxiv.orgCertifiably-Robust Federated Adversarial Learning via Randomized SmoothingC Chen, B Kailkhura, R Goldhahn…\xa0- 2021 IEEE 18th\xa0…, 2021 - ieeexplore.ieee.orgFederated learning is an emerging data-private distributed learning framework, which, however, is vulnerable to adversarial attacks. Although several heuristic defenses are\xa0…Save Cite Cited by 1 Related articles All 5 versions   
[PDF] arxiv.orgFederated learning in adversarial settingsR Kerkouche, G Ács, C Castelluccia\xa0- arXiv preprint arXiv:2010.07808, 2020 - arxiv.orgFederated Learning enables entities to collaboratively learn a shared prediction model while keeping their training data locally. It prevents data collection and aggregation and, therefore\xa0…Save Cite Cited by 5 Related articles All 6 versions  View as HTML  Privacy-enhanced federated learning against poisoning adversariesX Liu, H Li, G Xu, Z Chen, X Huang…\xa0- IEEE Transactions on\xa0…, 2021 - ieeexplore.ieee.orgFederated learning (FL), as a distributed machine learning setting, has received considerable attention in recent years. To alleviate privacy concerns, FL essentially\xa0…Save Cite Cited by 8 Related articles   
[PDF] arxiv.orgDynamic backdoor attacks against federated learningA Huang\xa0- arXiv preprint arXiv:2011.07429, 2020 - arxiv.orgFederated Learning (FL) is a new machine learning framework, which enables millions of participants to collaboratively train machine learning model without compromising data\xa0…Save Cite Cited by 5 Related articles All 3 versions  View as HTML  
[HTML] springer.com[HTML][HTML] Blockchain for federated learning toward secure distributed machine learning systems: a systemic surveyD Li, D Han, TH Weng, Z Zheng, H Li, H Liu…\xa0- Soft Computing, 2022 - SpringerFederated learning (FL) is a promising decentralized deep learning technology, which allows users to update models cooperatively without sharing their data. FL is reshaping\xa0…Save Cite Cited by 8 Related articles All 3 versions   
[PDF] nsf.govMitigating data poisoning attacks on a federated learning-edge computing networkR Doku, DB Rawat\xa0- 2021 IEEE 18th Annual Consumer\xa0…, 2021 - ieeexplore.ieee.orgEdge Computing (EC) has seen a continuous rise in its popularity as it provides a solution to the latency and communication issues associated with edge devices transferring data to\xa0…Save Cite Cited by 6 Related articles All 2 versions   
[PDF] aaai.orgA new ensemble adversarial attack powered by long-term gradient memoriesZ Che, A Borji, G Zhai, S Ling, J Li…\xa0- Proceedings of the AAAI\xa0…, 2020 - ojs.aaai.orgDeep neural networks are vulnerable to adversarial attacks. More importantly, some adversarial examples crafted against an ensemble of pre-trained source models can transfer\xa0…Save Cite Cited by 5 Related articles All 6 versions  View as HTML  
[PDF] arxiv.orgAdversarial training in communication constrained federated learningD Shah, P Dube, S Chakraborty, A Verma\xa0- arXiv preprint arXiv\xa0…, 2021 - arxiv.orgFederated learning enables model training over a distributed corpus of agent data. However, the trained model is vulnerable to adversarial examples, designed to elicit\xa0…Save Cite Cited by 6 Related articles All 4 versions  View as HTML  
[PDF] arxiv.orgProvable defense against privacy leakage in federated learning from representation perspectiveJ Sun, A Li, B Wang, H Yang, H Li, Y Chen\xa0- arXiv preprint arXiv\xa0…, 2020 - arxiv.orgFederated learning (FL) is a popular distributed learning framework that can reduce privacy risks by not explicitly sharing private data. However, recent works demonstrated that sharing\xa0…Save Cite Cited by 6 Related articles All 3 versions  View as HTML  
[PDF] arxiv.orgFat: Federated adversarial trainingG Zizzo, A Rawat, M Sinn, B Buesser\xa0- arXiv preprint arXiv:2012.01791, 2020 - arxiv.orgFederated learning (FL) is one of the most important paradigms addressing privacy and data governance issues in machine learning (ML). Adversarial training has emerged, so far, as\xa0…Save Cite Cited by 9 Related articles All 5 versions  View as HTML Previous12345678910Next12345678910HelpPrivacyTerms']
"""
#title_from_scholar_search_result('https://scholar.google.com/scholar?q=related:X_Nqm_kCPlQJ:scholar.google.com/&scioq=Certifiably-Robust+Federated+Adversarial+Learning+via+Randomized+Smoothing&hl=en&as_sdt=0,33')
