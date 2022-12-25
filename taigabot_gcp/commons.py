"""Module to hold the common assets."""
from taiga.exceptions import TaigaException


class MissingParameters(TaigaException):
    """Custom exception to report missing information from the HTTP payload."""


class SafeDictionary(dict):
    """Class to safely replace substrings when attempting to format a string.
    Used to give the parameters to `str.format` ignoring if the keys exist."""

    def __missing__(self, key):
        return "{" + key + "}"


def format_strings_in_dict(strings: dict, string_replacements: dict):
    """Replace all values in the first dict with the keys on the second one.
    If any of the values on `strings` expects an expression to replace its content,
    it will do so from the `string_replacements`.

    :param dict strings: Dict holding strings on its values.
    :param dict string_replacements: Dict with expressions.
    :return: The strings with their content replaced.
    """

    for key, value in strings.items():
        if isinstance(value, str):
            strings[key] = strings[key].format_map(SafeDictionary(string_replacements))

    return strings
