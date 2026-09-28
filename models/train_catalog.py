import sqlite3
from typing import TypeVar, Generic
from models.common import InvalidTimeError
from models.train import Train
import functools
import logging

logging.basicConfig(filename = 'app.log', level = logging.INFO, format = '%(asctime)s -  %(levelname)s - %(message)s')

def log_action(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f"Вызов функции: {func.__name__} с аргументами: {args}, {kwargs}")
        try:
            result = func(*args, **kwargs)
            logging.info(f"Функция {func.__name__}  выполнена успешно")
            return result
        except Exception as e:
            logging.error(f"Ошибка в функции {func.__name__}: {str(e)}", exc_info = True)
            raise
    return wrapper

def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance

T = TypeVar('T')

class ParametrPolimor(Generic[T]):
    def __init__(self, content: T):
        self.content = content

    def get_content(self) -> T:
        return self.content

CLASS_REGISTRY = {}

class RegistryMeta(type):
    def __new__(cls, name, bases, dct):
        new_class = super().__new__(cls, name, bases, dct)
        CLASS_REGISTRY[name] = new_class
        return new_class

class InfoMixin:
    def get_info(self):
        raise NotImplementedError("Метод get_info() должен быть реализован")

class UpdateMixin:
    def updating_db(self):
        print("Updating Data Base")

class DeleteMixin:
    def remove_train(self):
        print("Deleting train")

class TrainCatalog:
    def __init__(self):
        self.trains = []

    def add_train(self, number, route, departure_time, arrival_time):
        train = Train(number, route, departure_time, arrival_time)
        self.trains.append(train)

    def add_object(self, obj = ParametrPolimor):
        self.trains.append(obj)

    def update_train(self, number, new_route=None, new_departure_time=None, new_arrival_time=None):
        for train in self.trains:
            if train.get_number() == number:
                if new_route:
                    train.set_route(new_route)
                if new_departure_time:
                    train.set_departure_time(new_departure_time)
                if new_arrival_time:
                    train.set_arrival_time(new_arrival_time)
                return True
        return False

    def delete_train(self, number):
        for train in self.trains:
            if train.get_number() == number:
                self.trains.remove(train)
                return True
        return False

    def get_trains(self, strategy):
        return strategy.output(self.trains)

    def get_object(self):
        return [obj.get_content() for obj in self.trains]

    def get_all_objects(self):
            """Возвращает список всех объектов с указанием их типа."""
            return [f"{type(train).__name__}: {train.get_info()}" for train in self.trains]

@singleton
class TrainCatalogDb(UpdateMixin, DeleteMixin, metaclass=RegistryMeta):

    def __init__(self):
        self.conn = sqlite3.connect('trains.db')
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS trains (
                number TEXT PRIMARY KEY,
                route TEXT,
                departure_time TEXT,
                arrival_time TEXT
            )
        ''')
        self.conn.commit()

    @log_action
    def add_train(self, number = None, route = None, departure_time = None, arrival_time = None):
        if not self._validate_time(departure_time):
            raise InvalidTimeError
        if not self._validate_time(arrival_time):
            raise InvalidTimeError
        self.cursor.execute('''
            INSERT INTO trains (number, route, departure_time, arrival_time)
            VALUES (?, ?, ?, ?)
        ''', (number, route, departure_time, arrival_time))
        self.conn.commit()

    @log_action
    def update_train(self, number = None, new_route= None, new_departure_time = None, new_arrival_time = None):
        if new_route:
            self.cursor.execute('''
                UPDATE trains SET route = ? WHERE number = ?
                ''', (new_route, number))
        if new_departure_time:
            self.cursor.execute('''
                UPDATE trains SET departure_time = ? WHERE number = ?
                ''', (new_departure_time, number))
        if new_arrival_time:
            self.cursor.execute('''
                UPDATE trains SET arrival_time = ? WHERE number = ?
                ''', (new_arrival_time, number))
        self.conn.commit()
        self.updating_db()
        return self.cursor.rowcount > 0

    @log_action
    def delete_train(self, number):
        self.cursor.execute('''
            DELETE FROM trains WHERE number = ?
        ''', (number,))
        self.conn.commit()
        self.remove_train()
        return self.cursor.rowcount > 0

    @log_action
    def get_trains(self):
        self.cursor.execute('SELECT * FROM trains')
        trains = self.cursor.fetchall()
        return [f"Поезд {row[0]}, маршрут: {row[1]}, отправление: {row[2]}, прибытие: {row[3]}" for row in trains]

    @log_action
    def get_all_objects(self):
        self.cursor.execute('SELECT * FROM trains')
        trains = self.cursor.fetchall()
        return [f"Train: Поезд {row[0]}, маршрут: {row[1]}, отправление: {row[2]}, прибытие: {row[3]}" for row in trains]

    def __del__(self):
        self.conn.close()

    def _validate_time(self, time):
        try :
            hours, minutes = map(int, time.split(':'))
            return 0 <= hours < 24 and 0 <= minutes < 60
        except ValueError:
            return False

    @log_action
    def train_available(self, number):
        self.cursor.execute('SELECT * FROM trains WHERE number = ?', (number,))
        return self.cursor.fetchone()

def print_entity_info(entity):
    print(entity.get_info())
