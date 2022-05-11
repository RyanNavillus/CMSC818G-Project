from data_collection import *
import rec
from os.path import exists
import csv
from scholarly import scholarly, ProxyGenerator
import torch

# accessing stored user titles and abstracts
paper_abstract_tuples = []
with open('users_abstracts.csv', newline='', encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        row_lst = list(row.keys())
        title = row_lst[0]
        abstract = row_lst[1]
        paper_abstract_tuples.append((title, abstract))
# accessing stored corpus titles and abstracts
corpus_abstract_tuples = []
with open('corpus_abstracts.csv', newline='', encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        row_lst = list(row.keys())
        title = row_lst[0]
        abstract = row_lst[1]
        corpus_abstract_tuples.append((title, abstract))

# Get all (3) papers from my Zotero library
papers = paper_data_from_zotero()   # list of 3 paper dictionaries
profile = rec.UserProf()
if(exists("profile.pt")):
    profile = torch.load("profile.pt")

print(paper_abstract_tuples)


# Build a corpus of papers to recommend from
# For all papers, get the titles of all papers google scholar provides as related papers or cited by papers
# this ends up being 50 papers
title_list = [paper['data']['title'] for paper in papers]
#corpus_titles = get_related_papers(title_list)
corpus_papers = []
if(exists("corpus.pt")):
    corpus_papers = torch.load("corpus.pt")

""" # make list of tuples (title, abstract) for the corpus of related papers
corpus_abstract_tuples = []
for title in corpus_titles:
    abstract = text_from_google_scholar(title, True)
    corpus_abstract_tuples.append((title, abstract))

# make list of tuples (title, abstract) for the papers already in Zotero
paper_abstract_tuples = []
for paper in papers:
    abstract = text_from_paper_dict(paper, True)
    paper_abstract_tuples.append((paper['data']['title'], abstract)) """

# Create user profile from full text, summarization performed
for papero in paper_abstract_tuples:
    if(not profile.findPaperExists(papero[0])):
        found = False
        paper = None
        for i in corpus_papers:
          if(i.getTitle() == title):
              found = True
              paper = i
        if(found):
            profile.addPaper(paper)
        else:
            newPaper = rec.Paper(papero[1],papero[0],[],True)
            profile.addPaper(newPaper)
            print("paper added")
            print(papero[0])

# Create corpus of papers for recommendation from abstracts, no summarization performed
for title in corpus_abstract_tuples:
    found = False
    for i in corpus_papers:
       if(i.getTitle() == title[0]):
        found = True
    if (profile.findPaperVec(title[0]) is not None and not found):
        newPaper = rec.Paper(profile.findPaperVec(title[0]),title[0],[],vec=True)
        corpus_papers.append(newPaper)
        found = True
    if(not found):
        newPaper = rec.Paper(title[1],title[0],[],True)
        corpus_papers.append(newPaper)
        print("paper added")
        print(title[0])

rec.recommend(5,profile,corpus_papers)

""" # Create user profile from full text, summarization performed
for papero in papers:
    if(not profile.findPaperExists(papero['title'])):
        found = False
        paper = None
        for i in corpus_papers:
          if(i.getTitle() == paper['title']):
              found = True
              paper = i
              break
        if(found):
            profile.addPaper(paper)
        else:
            newPaper = rec.Paper(text_from_paper_dict(papero,False),papero['title'],[],False)
            profile.addPaper(newPaper)
            print("One paper added")

# Create corpus of papers for recommendation from abstracts, no summarization performed
for title in corpus_titles:
    found = False
    for i in corpus_papers:
       if(i.getTitle() == title):
        found = True
        break
    if (profile.findPaperVec(title) is not None):
        newPaper = rec.Paper(profile.findPaperVec(title),title,[],vec=True)
        corpus_papers.append(newPaper)
        found = True
    if(not found):
        newPaper = rec.Paper(text_from_google_scholar(title,False),title,[],False)
        corpus_papers.append(newPaper)
        print("One paper added")

rec.recommend(5,profile,corpus_papers) """
# make list of tuples (title, full paper text) for the corpus of related papers
""" corpus_fulltext_tuples = []
for title in corpus_titles:
    text = text_from_google_scholar(title, False)
    corpus_abstract_tuples.append((title, text))

# make list of tuples (title, full paper text) for the papers already in Zotero
paper_fulltext_tuples = []
for paper in papers:
    text = text_from_paper_dict(paper, False)
    paper_abstract_tuples.append((paper['data']['title'], text))
 """
torch.save(profile,"profile.pt")
torch.save(corpus_papers,"corpus.pt")