"""Module for the class ParametersHandler."""
import json
from typing import Optional

from .commons import format_strings_in_dict
from .commons import MissingParameters


class ParametersHandler:
    """Class to parse the incoming parameters, read the stored templates and
    merge them together.
    """

    def __init__(self, base_dir: Optional[str] = None):

        if base_dir is None:
            self.base_dir = ""
        else:
            self.base_dir = base_dir

            if not self.base_dir.endswith("/"):
                self.base_dir += "/"

    def parse_payload(self, payload):
        """Parse the payload from the incoming request. Load the necessary data and
        tinker it according to the received payload.

        :param payload: Dict containing information to generate a User Story.
        :return: The User Story parsed.
        """

        if payload is None:
            raise MissingParameters("Empty payload")

        if "filename" in payload:
            filename = payload["filename"]
        else:
            raise MissingParameters("Missing 'filename' attribute in the HTTP payload")

        data = self.parse_user_story_from_json(filename)

        if "user_stories" in data:
            full_user_stories = []
            for user_story in data["user_stories"]:
                full_user_stories.append(
                    self._parse_single_user_story(user_story, payload)
                )

            data["user_stories"] = full_user_stories
        else:
            data = self._parse_single_user_story(data, payload)

        return data

    def _parse_single_user_story(self, data, payload):

        if "data" in payload:
            data = {**data, **payload["data"]}

        self.__assert_parameter(data, "project_slug")
        self.__assert_parameter(data, "subject")

        if "string_replacement" in payload:
            data = format_strings_in_dict(data, payload["string_replacement"])

        return data

    @staticmethod
    def __assert_parameter(data, parameter):
        if parameter not in data:
            raise MissingParameters(
                f"Missing '{parameter}' attribute in User Story. "
                f"Modify the template or send 'data.{parameter}' in the HTTP payload"
            )

    def parse_user_story_from_json(self, filename: str):
        """Parse the content of a JSON file.

        :param str filename: The file to parse.
        :return: The content of the file, which should be a JSON.
        """

        # Read data from file
        with open(self.base_dir + filename, encoding="utf-8") as file:
            return json.load(file)
