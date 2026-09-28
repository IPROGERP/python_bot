from models.common import InvalidTimeError, Transport


class Train(Transport):

    __slots__ = ['number', 'route', 'departure_time', 'arrival_time']

    def __init__(self, number, route, departure_time, arrival_time):
        super().__init__(number, "Train", route)
        if not self._validate_time(departure_time):
            raise InvalidTimeError
        self.__departure_time = departure_time
        if not self._validate_time(arrival_time):
            raise InvalidTimeError
        self.__new_arrival_time = arrival_time
        self._number = number

    def _validate_time(self, time):
        try :
            hours, minutes = map(int, time.split(':'))
            return 0 <= hours < 24 and 0 <= minutes < 60
        except ValueError:
            return False

    def get_info(self):
        return f"Поезд {self._id}, маршрут: {self._route}, отправление: {self.__departure_time}, прибытие: {self.__new_arrival_time}"

    def set_route(self, new_route):
        self.__route = new_route

    def set_departure_time(self, new_departure_time):
        if not self._validate_time(new_departure_time):
            raise InvalidTimeError
        self.__departure_time = new_departure_time

    def set_arrival_time(self, new_arrival_time):
        if not self._validate_time(new_arrival_time):
            raise InvalidTimeError
        self.new_arrival_time = new_arrival_time

    def get_number(self):
        return self._number

class Bus(Transport):

    __slots__ = ['number', 'route', 'departure_time', 'arraival_time']

    def __init__(self, number, route, departure_time, arrival_time):
        super().__init__(number, "Train", route)
        if not self._validate_time(departure_time):
            raise InvalidTimeError
        self.__departure_time = departure_time
        if not self._validate_time(arrival_time):
            raise InvalidTimeError
        self.__new_arrival_time = arrival_time

    def _validate_time(self, time):
        try :
            hours, minutes = map(int, time.split(':'))
            return 0 <= hours < 24 and 0 <= minutes < 60
        except ValueError:
            return False

    def get_info(self):
        return f"Поезд {self._id}, маршрут: {self._route}, отправление: {self.__departure_time}, прибытие: {self.__new_arrival_time}"

    def set_route(self, new_route):
        self.__route = new_route

    def set_departure_time(self, new_departure_time):
        if not self._validate_time(new_departure_time):
            raise InvalidTimeError
        self.__departure_time = new_departure_time

    def set_arrival_time(self, new_arrival_time):
        if not self._validate_time(new_arrival_time):
            raise InvalidTimeError
        self.new_arrival_time = new_arrival_time

    def get_number(self):
        return self.__number
