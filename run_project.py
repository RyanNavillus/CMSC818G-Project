from data_collection import paper_data_from_zotero, get_related_papers, text_from_google_scholar, text_from_paper_dict, add_title_to_zotero
from scholarly import scholarly, ProxyGenerator
from os.path import exists
import torch
import rec
import configparser


def get_recommendations(project_id):
    zotero_id = int(config["Zotero"]["ID"])
    zotero_library = config["Zotero"]["library"]
    zotero_key = config["Zotero"]["API_KEY"]
    papers = paper_data_from_zotero(zotero_id, zotero_library, zotero_key)   # list of 3 paper dictionaries
    if exists("profile.pt"):
        profile = torch.load("profile.pt")
    else:
        profile = rec.UserProf()

    # List paper titles
    title_list = [paper['data']['title'] for paper in papers]

    # Collect related papers
    corpus_titles = get_related_papers(title_list)

    # Collect abstracts for related papers
    corpus_abstract_tuples = []
    for title in corpus_titles:
        abstract = text_from_google_scholar(title, True)
        corpus_abstract_tuples.append((title, abstract))

    if exists("corpus.pt"):
        corpus_papers = torch.load("corpus.pt")
    else:
        corpus_papers = []

    # Find papers in paper list and add to corpus
    for title, abstract in corpus_abstract_tuples:
        found = False
        for paper in corpus_papers:
            if paper.getTitle() == title:
                found = True
        if profile.findPaperVec(title) is not None and not found:
            newPaper = rec.Paper(profile.findPaperVec(title), title, [], vec=True)
            corpus_papers.append(newPaper)
            found = True
        if not found:
            newPaper = rec.Paper(abstract, title, [], True)
            corpus_papers.append(newPaper)
            print(f"{title[0]} added to corpus")

    # Generate recommendations
    recs = rec.recommend(3, profile, corpus_papers)
    titles_for_zotero = []
    print("\nRecommended:")
    for recommendation in recs:
        title = recommendation.getTitle()
        print(title)
        titles_for_zotero.append(title)
    print("")

    # Add recommended papers to Zotero
    add_title_to_zotero(titles_for_zotero, zotero_id, zotero_library, zotero_key)

    # Save corpus and profile for next time
    torch.save(profile, "profile.pt")
    torch.save(corpus_papers, "corpus.pt")

def write_config():
    with open("config.ini", "w") as configfile:
        config.write(configfile)


config = configparser.ConfigParser()
config.read('config.ini')

# Initialize general settings if necessary
if "General" not in config:
    config["General"] = {}
    config["General"]["numProjects"] = str(0)
num_projects = int(config["General"]["numProjects"])


# Initialize Zotero settings if necessary
if "Zotero" not in config:
    zotero_id = input("Please type zotero id: ")
    zotero_library = input("Please type zotero library name: ")
    zotero_key = input("Please type zotero API key: ")
    config["Zotero"] = {}
    config["Zotero"]["ID"] = zotero_id
    config["Zotero"]["library"] = zotero_library
    config["Zotero"]["API_KEY"] = zotero_key
    write_config()

# Set up initial project if necessary
if num_projects == 0:
    print("Set up a project to begin getting recommendations.")
    project_name = input("Choose a project name: ")
    config["Project 1"] = {}
    config["Project 1"]["name"] = project_name
    config["General"]["numProjects"] = str(1)
    write_config()

while True:
    # Choose action
    action = input("\n1. Create new project\n2. Get recommendations\n3. Exit\nSelect which action you would like to perform: ")
    if action == str(1):
        project_name = input("Choose a project name: ")
        config[f"Project {num_projects+1}"] = {}
        config[f"Project {num_projects+1}"]["name"] = project_name
        config["General"]["numProjects"] = str(num_projects+1)
        write_config()

    if action == str(2):
        project_list = ""
        for i in range(int(config["General"]["numProjects"])):
            project_name = config[f"Project {i+1}"]["name"]
            project_list += f"{i+1}. {project_name}\n"
        project_id = input(project_list + "Select project id: ")
        get_recommendations(project_id)
        print(config[f"Project {project_id}"]["name"])

    if action == str(3):
        write_config()
        break


