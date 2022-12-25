import json

from commons import MissingParameters, SafeDictionary


class ParametersHandler:

    def __init__(self, base_dir: str=None):

        if base_dir is None:
            self.base_dir = ""
        else:
            self.base_dir = base_dir

            if not self.base_dir.endswith("/"):
                self.base_dir += "/"

    def parse_payload(self, payload):

        if payload is None:
            raise MissingParameters("Empty payload")

        if 'filename' in payload:
            filename = payload['filename']
        else:
            raise MissingParameters(f"Missing 'filename' attribute in the "
                                    f"HTTP payload")

        data = self.parse_user_story_from_json(filename)

        if 'user_stories' in data:
            full_user_stories = []
            for user_story in data['user_stories']:
                full_user_stories.append(
                    self._parse_single_user_story(user_story, payload))

            data['user_stories'] = full_user_stories
        else:
            data = self._parse_single_user_story(data, payload)

        return data

    def _parse_single_user_story(self, data, payload):

        if 'data' in payload:
            data = {**data, **payload['data']}

        self.__assert_parameter(data, 'project_slug')
        self.__assert_parameter(data, 'subject')

        if 'string_replacement' in payload:
            data = self.replace_strings_in_dict(data, payload['string_replacement'])

        return data

    @staticmethod
    def __assert_parameter(data, parameter):
        if parameter not in data:
            raise MissingParameters(
                f"Missing '{parameter}' attribute in User Story. Modify the template "
                f"or send 'data.{parameter}' in the HTTP payload")

    def parse_user_story_from_json(self, filename: str):
        """Parse the content of a JSON file.

        Args:
            filename (str): The file to parse.
        """

        # Read data from file
        with open(self.base_dir + filename) as file:
            return json.load(file)

    @staticmethod
    def replace_strings_in_dict(user_story, string_replacements):

        for key, value in user_story.items():
            if isinstance(value, str):
                user_story[key] = user_story[key].format_map(SafeDictionary(string_replacements))

        return user_story
