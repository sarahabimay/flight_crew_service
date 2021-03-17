import os
import json

class Repository():
    def __init__(self, location):
        self.location = os.path.expanduser(location)
        self.load(self.location)

    def load(self, location):
        if os.path.exists(location):
            self._load()
        else:
            self.db = {}

    def _load(self):
        self.db = json.load(open(self.location, "r"))

    def writedb(self):
        try:
            json.dump(self.db, open(self.location, "w+"), allow_nan=False)
            return True
        except:
            return False
