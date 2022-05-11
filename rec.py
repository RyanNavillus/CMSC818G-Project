import torch
import torch.nn.functional as F
from queue import PriorityQueue
from transformers import AutoTokenizer, AutoModel
from summarizer import Summarizer
from nltk import tokenize
import numpy as np

tokenizer = AutoTokenizer.from_pretrained('allenai/scibert_scivocab_uncased')
model = AutoModel.from_pretrained('allenai/scibert_scivocab_uncased')
summarizer = Summarizer()

def list_intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3

class Paper:
    textTokens = None
    title = None
    keywords = []
    vec = None 
    
    def __init__(self,txt, title,kwds,abstract=False,vec=False):
        if(not vec):
            summary = txt if abstract else summarizer(txt) #Slow, but Out of memory without summarization
            summarySent = tokenize.sent_tokenize(summary)
            self.textTokens = tokenizer(summarySent,return_tensors="pt",padding=True,truncation=True,max_length=512)
            self.title = title
            self.keywords = kwds
            vecs = model(**self.textTokens)
            self.vec = torch.mean(vecs.pooler_output, axis=0)
        else:
            self.title = title
            self.keywords = kwds
            self.vec = txt

    def getTitle(self):
        return self.title

    def vectorize(self):
        if(self.vec is None):
            self.vec = model(**self.textTokens)


class UserProf:
    keywords = None
    vec = []
    titles = []

    def __init__(self,kwd=None):
        self.keywords = kwd

    def addPaper(self, paper):
        self.vec.append(paper.vec)
        self.titles.append(paper.title)

    def findPaperExists(self,title):
        for i in self.titles:
            if (title == i):
                return True 
        return False

    
    def findPaperVec(self,title):
        for i in range(0,len(self.titles)):
            if (title == self.titles[i]):
                return self.vec[i]
        return None



class recommendations:
    paperTitle = None
    similarity = 0.0
    def __init__(self, title, sim):
        self.paperTitle = title
        self.similarity = sim

    def __gt__(self, other):
        return self.similarity > other.similarity

    def __eq__(self, other):
        return self.similarity == other.similarity

    def getTitle(self):
        return self.paperTitle

def recommend(num, uProf:UserProf, papers):
    recommended = PriorityQueue()
    for i in papers:
        if(uProf.keywords == None or list_intersection(uProf.keyword,i.keywords)):
            similarity = 0
            for j in uProf.vec:
                similarity += F.cosine_similarity(j,i.vec,dim=0)
            rec = recommendations(i.title,similarity)
            recommended.put(rec)
            if(recommended.qsize() > num):
                recommended.get()
    return recommended

    