
from taiga.exceptions import TaigaException


class MissingParameters(TaigaException):
    pass


class SafeDictionary(dict):
    def __missing__(self, key):
        return '{' + key + '}'
