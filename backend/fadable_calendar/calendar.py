



class Calendar:
    def __init__(self, name):
        self.name = name
        self.events = []

    def add_event(self, event):
        self.events.append(event)

    def get_events(self):
        return self.events
