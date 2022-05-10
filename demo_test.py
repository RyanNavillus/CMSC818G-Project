from data_collection import *
import rec

# Get all (3) papers from my Zotero library
papers = paper_data_from_zotero()   # list of 3 paper dictionaries
profile = rec.UserProf()


# Build a corpus of papers to recommend from
# For all papers, get the titles of all papers google scholar provides as related papers or cited by papers
# this ends up being 50 papers
title_list = [paper['data']['title'] for paper in papers]
corpus_titles = get_related_papers(title_list)
corpus_papers = []

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

# Create user profile from abstracts, no summarization performed
# for paper in papers:
#     newPaper = rec.Paper(text_from_paper_dict(paper,True),paper['title'],[],True)
#     profile.addPaper(newPaper)
# Create corpus of papers for recommendation from abstracts, no summarization performed
# for title in corpus_titles:
#     newPaper = rec.Paper(text_from_google_scholar(title,True),title,[],True)
#     corpus_papers.append(newPaper)

# rec.recommend(5,profile,corpus_papers)

# Create user profile from full text, summarization performed
for paper in papers:
    newPaper = rec.Paper(text_from_paper_dict(paper,False),paper['title'],[],False)
    profile.addPaper(newPaper)
# Create corpus of papers for recommendation from abstracts, no summarization performed
for title in corpus_titles:
    newPaper = rec.Paper(text_from_google_scholar(title,False),title,[],False)
    corpus_papers.append(newPaper)

rec.recommend(5,profile,corpus_papers)
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