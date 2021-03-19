from .repository import Repository


class CrewRepository(Repository):
    def __init__(self, location):
        Repository.__init__(self, location)

    def crew(self):
        return self.db['Crew'] if self.db else []

