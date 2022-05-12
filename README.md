# RAGS: Research Assistant for Graduate Students

## Instructions
### Installing necessary packages
- follow [setup instructions for pyzotero](https://pyzotero.readthedocs.io/en/latest/)
- follow [setup instuctions for scholarly](https://github.com/scholarly-python-package/scholarly/blob/main/docs/quickstart.rst)

# Usage
To use the project, run the `run_project` script:
```
python run_project.py
```

This will take you through setting up your user profile and first project. You will need to get and API key and the name of your personal zotero library using the instructions for [pyzotero](https://pyzotero.readthedocs.io/en/latest/#getting-started-short-version). These configurations are stored in `config.ini` and can be edited at any time.

After configuration, the script will provide you with the options of creating a new project, getting recommendations for an existing project, or exiting the application. Any papers searched during the process of producing recommendations will be added to a growing corpus, which is used to provide recommendations more quickly in the future. This corpus is saved in `corpus.pt`.
