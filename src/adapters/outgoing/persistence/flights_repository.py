from .repository import Repository


class FlightsRepository(Repository):
    def __init__(self, location):
        Repository.__init__(self, location)

    def flights(self):
        return self.db

    def append(self, new_flight):
        self.db.append(new_flight)
        self.writedb()
