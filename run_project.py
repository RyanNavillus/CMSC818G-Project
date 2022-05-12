import configparser
config = configparser.ConfigParser()

config.read('config.ini')

if "General" not in config:
    config["General"] = {}
    config["General"]["numProjects"] = str(0)


if "Zotero" not in config:
    zotero_id = input("Please type zotero id: ")
    zotero_library = input("Please type zotero library name: ")
    zotero_key = input("Please type zotero API key: ")
    config["Zotero"] = {}
    config["Zotero"]["ID"] = zotero_id
    config["Zotero"]["library"] = zotero_library
    config["Zotero"]["API_KEY"] = zotero_key

if config["General"]["numProjects"] == str(0):
    print("Set up a project to begin getting recommendations.")
    project_name = input("Choose a project name: ")
    config["Project 1"] = {}
    config["Project 1"]["name"] = project_name
    config["General"]["numProjects"] = str(1)

project_list = ""
for i in range(int(config["General"]["numProjects"])):
    project_name = config[f"Project {i+1}"]["name"]
    project_list += f"{i+1}. {project_name}\n"
project_id = input(project_list + "Select project id: ")
print(config[f"Project {project_id}"]["name"])


with open("config.ini", "w") as configfile:
    config.write(configfile)
