

class EventListener:
    def __init__(self):
        self.handlers = {}

    def register(self, event, handler):
        self.handlers[event] = handler

    def update(self, event, data):
        if event not in self.handlers:
            return
        
        return self.handlers[event](data)
