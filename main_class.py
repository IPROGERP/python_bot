from models.train_catalog import TrainCatalog, TrainCatalogDb
from models.train import Train, Bus


class User():
    def update(self, message):
        print(f"Message :  {message}")

class Subject():
    def __init__(self):
        self._users = []

    def add_user(self, user):
        self._users.append(user)

    def remove_user(self, user):
        self._users.remove(user)

    def notify(self):
        for user in self._users:
            user.update("I caught message")

class ReturnAsNormal():
    @staticmethod
    def output(trains):
        return [train.get_info() for train in trains]

class ReturnReversed():
    @staticmethod
    def output(trains):
        return [train.get_info() for train in reversed(trains)]

class ReturnSorted():
    @staticmethod
    def output(trains):
        sorted_trains = sorted(trains, key = lambda train : train.get_number())
        return [train.get_info() for train in sorted_trains]


class CatalogFactory():
    @staticmethod
    def create_catalog(catalog_type, *args):
        if catalog_type == 'CatalogDb':
            return TrainCatalogDb(*args)
        if catalog_type == 'Catalog':
            return TrainCatalog(*args)

class TransportFactory():
    @staticmethod
    def create_transport(transport_type, *args):
        if transport_type == 'train':
            return Train(*args)
        if transport_type == 'bus':
            return Bus(*args)
