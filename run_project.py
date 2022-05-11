import configparser
config = configparser.ConfigParser()

config.read('config.ini')
if "Zotero" not in config:
    zotero_id = input("Please type zotero id: ")
    zotero_library = input("Please type zotero library name: ")
    zotero_key = input("Please type zotero API key: ")
    config["Zotero"] = {}
    config["Zotero"]["ID"] = zotero_id
    config["Zotero"]["library"] = zotero_library
    config["Zotero"]["API_KEY"] = zotero_key

if "Projects" not in config:
    config["Projects"] = {}
    print("Set up a project to begin getting recommendations.")
    project_name = input("Choose a project name: ")
    config["Projects"]["1"] = project_name

project_list = ""
for i, project in enumerate(config["Projects"]):
    project_list += f"{i+1}. {project}\n"
project_id = input(project_list + "Select project id: ")
print(config["Projects"][project_id])


with open("config.ini", "w") as configfile:
    config.write(configfile)
