from datetime import datetime


class Activity:

    def __init__(self, name, detection):
        self.name = name
        self.detection = detection
        self.relevant_fields = self.get_relevant_fields()

    def get_relevant_fields(self):
        # TODO: Implement
        return []


class Field:

    def __init__(self, name):
        self.name = name


class Paper:

    def __init__(self, title, venue, url, last_read=None):
        self.title = title
        self.venue = venue
        self.url = url
        self.last_read = last_read if last_read else datetime.now()
        self.authors = self.get_authors()
        self.field = self.get_fields()

    def get_authors(self):
        # TODO: Implement
        return []

    def get_fields(self):
        # TODO: Implement
        return []


class Researcher:

    def __init__(self, name, homepage, email, affiliations):
        self.name = name
        self.homepage = homepage
        self.email = email
        self.affiliations = affiliations
        self.publications = self.get_publications()
        self.collaborators = self.get_collaborators()
        self.fields = self.get_fields()

    def get_publications(self):
        # TODO: Implement
        return []

    def get_collaborators(self):
        # TODO: Implement
        return []

    def get_fields(self):
        # TODO: Implement
        return []


class User(Researcher):

    def __init__(self, name, email, homepage, affiliations, field_names):
        self.name = name
        self.email = email
        self.homepage = homepage
        self.affiliations = affiliations
        super().__init__(name, homepage, email, affiliations)
        self.fields = []
        for field_name in field_names:
            self.fields.append(Field(field_name))
        self.papers = self.get_papers()

    def get_papers(self):
        # TODO: Implement
        return []

    def recommend_collaborators(self):
        # TODO: Implement
        return []

    def recommend_papers(self):
        # TODO: Implement
        return []

    def recommend_activities(self):
        # TODO: Implement
        return []

    def save_user(self):
        with open("user.txt", "w") as user_file:
            user_file.write(self.name + "\n")
            user_file.write(self.email + "\n")
            user_file.write(self.homepage + "\n")
            user_file.write(self.affiliations + "\n")
            for field in self.fields[-1]:
                user_file.write(field.anme + ", ")
            user_file.write(self.fields[-1].name + "\n")
            # TODO: Save papers

    def load_user(self):
        with open("user.txt", "r") as user_file:
            self.name = user_file.readline()
            self.email = user_file.readline()
            self.homepage = user_file.readline()
            # TODO: Load affiliations, fields, and papers
