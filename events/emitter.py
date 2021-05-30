

class Emitter:
    def __init__(self):
        self.listeners = []

    def register(self, listener):
        self.listeners.append(listener)

    def emit(self, event, data):
        for listener in self.listeners:
            listener.update(event, data)

