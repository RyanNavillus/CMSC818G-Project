from data_collection import paper_data_from_zotero, get_related_papers, text_from_google_scholar, text_from_paper_dict
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
        title = row['title']
        abstract = row['abstract']
        paper_abstract_tuples.append((title, abstract))



# accessing stored corpus titles and abstracts
corpus_abstract_tuples = []
with open('corpus_abstracts.csv', newline='', encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        title = row['title']
        abstract = row['abstract']
        corpus_abstract_tuples.append((title, abstract))

# personal library ID
ID = 8601934
LIBRARY = 'user'
APIKEY = 'CzACnmlnHkQxIbkjj1y2tNzu'

# Get all (3) papers from my Zotero library
papers = paper_data_from_zotero(ID, LIBRARY, APIKEY)   # list of 3 paper dictionaries
profile = rec.UserProf()
if(exists("profile.pt")):
    profile = torch.load("profile.pt")



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
          if(i.getTitle() == papero[0]):
              found = True
              paper = i
        if(found):
            profile.addPaper(paper)
        else:
            newPaper = rec.Paper(papero[1],papero[0],[],True)
            profile.addPaper(newPaper)


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
        print(title[0])
        print("paper added to corpus")

recs = rec.recommend(3,profile,corpus_papers)
titles_for_zotero = []
print("Recommended:")
for i in recs:
    title = i.getTitle()
    print(title)
    titles_for_zotero.append(title)

# Add recommended papers to Zotero
add_title_to_zotero(titles_for_zotero)

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

<<<<<<< HEAD
# Create user profile from full text, summarization performed
for paper in papers:
    newPaper = rec.Paper(text_from_paper_dict(paper, False), paper['title'], [], False)
    profile.addPaper(newPaper)
# Create corpus of papers for recommendation from abstracts, no summarization performed
for title in corpus_titles:
    newPaper = rec.Paper(text_from_google_scholar(title, False), title, [], False)
    corpus_papers.append(newPaper)

rec.recommend(5, profile, corpus_papers)
=======
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
