from data_collection import *

# Get all (3) papers from my Zotero library
papers = paper_data_from_zotero()   # list of 3 paper dictionaries

corpus_titles = ['Attack-resistant federated learning with residual-based reweighting',
                 'Mitigating backdoor attacks in federated learning',
                 'Baffle: Backdoor detection via feedback-based federated learning',
                 'Can you really backdoor federated learning?',
                 'Learning to detect malicious clients for robust federated learning',
                 'Robust aggregation for federated learning',
                 'ssCrfl: Certifiably robust federated learning against backdoor attacks',
                 'Dba: Distributed backdoor attacks against federated learning',
                 'Backdoor attacks and defenses in feature-partitioned collaborative learning',
                 #'ttack of the tails',
                 'Certifiably-Robust Federated Adversarial Learning via Randomized Smoothing',
                 'Federated learning in adversarial settings',
                 'Blockchain for federated learning toward secure distributed machine learning systems: a systemic survey',
                 #'Dynamic backdoor attacks against federated learningA Huang\xa0- arXiv preprin',
                 'Mitigating data poisoning attacks on a federated learning-edge computing network',
                 'A new ensemble adversarial attack powered by long-term gradient memories',
                 'Adversarial training in communication constrained federated learning',
                 'Provable defense against privacy leakage in federated learning from representation perspective',
                 'Fat: Federated adversarial training', 'Data poisoning attacks against federated learning systems',
                 'Local Model Poisoning Attacks to {Byzantine-Robust} Federated Learning',
                 'Mitigating backdoor attacks in federated learning',
                 'Data poisoning attacks on federated machine learning',
                 'Can you really backdoor federated learning?',
                 'The limitations of federated learning in sybil settings',
                 'Mitigating sybils in federated learning poisoning',
                 #'', '', '',
                 'Learning to detect malicious clients for robust federated learning',
                 'Dba: Distributed backdoor attacks against federated learning']

####### INITIAL IMPLEMENTATION, WHICH IS UNRELIABLE DUE TO SCHOLARLY ISSUES #######

# Build a corpus of papers to recommend from
# For all papers, get the titles of all papers google scholar provides as related papers or cited by papers
# this ends up being 50 papers
"""title_list = [paper['data']['title'] for paper in papers]
corpus_titles = get_related_papers(title_list)"""

# make list of tuples (title, abstract) for the corpus of related papers
"""corpus_abstract_tuples = []
for title in corpus_titles:
    print(title)
    abstract = text_from_google_scholar(title, True)
    corpus_abstract_tuples.append((title, abstract))"""

# make list of tuples (title, abstract) for the papers already in Zotero
"""paper_abstract_tuples = []
for paper in papers:
    abstract = text_from_paper_dict(paper, True)
    paper_abstract_tuples.append((paper['data']['title'], abstract))"""

# make list of tuples (title, full paper text) for the corpus of related papers
"""corpus_fulltext_tuples = []
for title in corpus_titles:
    text = text_from_google_scholar(title, False)
    corpus_abstract_tuples.append((title, text))"""

# make list of tuples (title, full paper text) for the papers already in Zotero
"""paper_fulltext_tuples = []
for paper in papers:
    text = text_from_paper_dict(paper, False)
    paper_abstract_tuples.append((paper['data']['title'], text))"""
