import pickle
from stock_data_examples.utils.ConfigsParameters import *

class Persistable:

    def persist(self, name):
         with open(configs["persisted_objects_folderpath"] + name + ".pkl", 'wb') as output:
            pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)

    def to_object_string(self):
        object_string = pickle.dumps(self)
        return object_string

    @staticmethod
    def load(name):
        try:
            with open(configs["persisted_objects_folderpath"] + name + ".pkl", 'rb') as input:
                loadedObject = pickle.load(input)
            return loadedObject
        except Exception as e:
            print("No persisted object exists.")
            return e