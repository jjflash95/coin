from abc import ABC, ABCMeta, abstractmethod
import json


class Jsonifyable(metaclass=ABCMeta):
    @abstractmethod
    def to_dict(self):
        pass

    def to_json(self):
        return self.jsonify(self.to_dict())

    def jsonify(self, data):
        return json.dumps(data, sort_keys=True)