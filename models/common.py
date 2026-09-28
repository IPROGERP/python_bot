class InvalidTimeError(Exception):
    """Invalid Time Error"""
    pass

class Transport:
    def __init__(self, id, name, route):
        self._id = id
        self._name = name
        self._route = route

    def get_info(self):
        return f"Id : {self._id}, Name : {self._name}, Route : {self._route}"
