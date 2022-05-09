from data_collection import *

# Get all (3) papers from my Zotero library
papers = paper_data_from_zotero()   # list of 3 paper dictionaries

# Build a corpus of papers to recommend from
# For all papers, get the titles of all papers google scholar provides as related papers or cited by papers
# this ends up being 50 papers
title_list = [paper['data']['title'] for paper in papers]
corpus_titles = get_related_papers(title_list)

# make list of tuples (title, abstract) for the corpus of related papers
corpus_abstract_tuples = []
for title in corpus_titles:
    abstract = text_from_google_scholar(title, True)
    corpus_abstract_tuples.append((title, abstract))

# make list of tuples (title, abstract) for the papers already in Zotero
paper_abstract_tuples = []
for paper in papers:
    abstract = text_from_paper_dict(paper, True)
    paper_abstract_tuples.append((paper['data']['title'], abstract))

# make list of tuples (title, full paper text) for the corpus of related papers
corpus_fulltext_tuples = []
for title in corpus_titles:
    text = text_from_google_scholar(title, False)
    corpus_abstract_tuples.append((title, text))

# make list of tuples (title, full paper text) for the papers already in Zotero
paper_fulltext_tuples = []
for paper in papers:
    text = text_from_paper_dict(paper, False)
    paper_abstract_tuples.append((paper['data']['title'], text))
