
from contextlib import suppress
from typing import Dict, Optional

from taiga import TaigaAPI
from taiga.models import models

from commons import TaigaException


class TaigaBot(TaigaAPI):

    @staticmethod
    def __get_user_id_from_username(
            project: models.Project, username: str
    ) -> Optional[int]:
        """Get the user id from the username.
        If the user is not found, return None.

        Args:
            project (models.Project): The TaigaAPI representation of a Taiga project.
            username (str): The User's username to look for.

        Returns:
            Optional[int]: The User's id, if found.
        """
        for user in project.members:
            if user.username == username:
                return user.id
        else:
            return None

    @staticmethod
    def __get_status_id_from_slug(
            project: models.Project, status_slug: Optional[str]
    ) -> int:
        """Get the status id from the status slug.
        If the `status_slug` is None or it's not found, the default User Story Status id will be returned.

        Args:
            project (models.Project): The TaigaAPI representation of a Taiga project.
            status_slug (Optional[str]): The status slug of the status id to retrieve.

        Returns:
            int: The status id.
        """
        if status_slug is None:
            return project.default_us_status

        for status in project.us_statuses:
            if status.slug == status_slug:
                return status.id
        else:
            return project.default_us_status

    def _build_user_story_parameters(
        self, project: models.Project, data: Dict
    ) -> Dict[str, str]:
        """Build the API request parameters to create a User Story from the Project and
        User Story information.

        From `data`, the field 'subject' is mandatory. It also accepts 'description', 'assigned_to',
        'tags' and 'status'.

        Args:
            project (models.Project): The TaigaAPI representation of a Taiga project.
            data (Dict): The User Story information.

        Returns:
            Dict[str, str]: The parameters to send on the API call to create the User Story object.
        """
        # Initialize User Story parameters
        parameters = {"subject": data['subject']}

        # Retrieve description if defined
        if 'description' in data:
            parameters["description"] = data['description']

        # Retrieve assignee if defined and exists
        if 'assignee' in data:
            user_id = self.__get_user_id_from_username(project, data['assignee'])
            if user_id is not None:
                parameters["assigned_to"] = user_id

        if 'tags' in data:
            parameters["tags"] = data['tags']

        # Retrieve status if defined or use the default one
        if 'status' in data:
            status_slug = data['status']
        else:
            status_slug = None

        status_id = self.__get_status_id_from_slug(project, status_slug)
        parameters["status"] = status_id

        return parameters

    def _build_task_parameters(
        self, project: models.Project, data: Dict
    ) -> Dict[str, str]:
        """Build the API request parameters to create a Task from the Project and Task information.
        It also accepts the User Story assignee to fallback to as the Task assignee if none is
        specified.

        From `data`, the field 'subject' is mandatory. It also accepts 'us_order' and 'tags'.

        Args:
            project (models.Project): The TaigaAPI representation of a Taiga project.
            data (Dict): The Task information.

        Returns:
            Dict[str, str]: The parameters to send on the API call to create the Task object.
        """
        # Define the default parameters
        parameters = {"subject": data['subject'], "status": project.default_task_status}

        # Retrieve order if defined
        if 'order' in data:
            parameters["us_order"] = data['order']

        if 'tags' in data:
            parameters["tags"] = data['tags']

        # Retrieve assignee if defined
        if 'assignee' in data:
            user_id = self.__get_user_id_from_username(project, data['assignee'])
            parameters["assigned_to"] = user_id

        return parameters

    def create_user_story_from_dict(self, data: Dict) -> None:
        """Create a User Story from a Dict.

        The input data is expected to have the attributes 'project_slug' and 'subject',
        as they're the only mandatory fields to create a User Story.
        Additionally it may contain the 'description', 'assigned_to' and 'status' fields.

        It may also have an array 'tasks' to add Task objects to the User Story.
        Each Task must be have a 'subject' and might contain 'us_order' and 'assigned_to'.
        If no assignee is given for a Task, it will fall back to the User Story assignee.

        Args:
            data (Dict): The object with the User Story information.
        """

        # Get object Project
        try:
            project = self.projects.get_by_slug(data['project_slug'])
        except TaigaException:
            raise TaigaException(f'Project "{data["project_slug"]}" not found or '
                                 f'unauthorized.')

        # Build the User Story parameters from the data in the file
        parameters = self._build_user_story_parameters(project, data)

        # Create the User Story
        user_story = project.add_user_story(**parameters)
        print(f'Created User Story ({user_story.ref}): "{user_story.subject}"')

        print(data)
        # Check if there are Tasks to be created
        if "tasks" in data:
            for task in data['tasks']:

                # Build the Task parameters from the data in each of the `tasks` values
                parameters = self._build_task_parameters(project, task)

                # Create the Task
                task = user_story.add_task(**parameters)
                print(
                    f'Created Task ({task.ref}) on User Story ({user_story.ref}): '
                    f'"{task.subject}" '
                )

    def build_user_story(self, data: Dict) -> None:
        """Build the User Story from the received data.
        It takes into account that a single Dict might contain the User Story to create,
        or an array 'user_stories' with multiple User Story objects.

        Args:
            data (Dict): The User Story(ies) to create.
        """

        if 'user_stories' in data:
            # If there are multiple User Stories within the received object, create
            # each out individually.
            for user_story in data['user_stories']:
                self.create_user_story_from_dict(user_story)
        else:
            # If there's a single User Story, create it.
            self.create_user_story_from_dict(data)
