"""Main module. The `main` method will receive the HTTP request and handle it."""
from os import environ

import functions_framework

from taigabot_gcp.commons import TaigaException
from taigabot_gcp.parameters_handler import ParametersHandler
from taigabot_gcp.taiga_bot import TaigaBot


@functions_framework.http
def main(request):
    """HTTP Cloud Function.
    Args:
       request (flask.Request): The request object.
       <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
       The response text, or any set of values that can be turned into a
       Response object using `make_response`
       <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """

    try:
        # Initialize the bot
        taigabot = TaigaBot(
            host=environ.get("TAIGA_DOMAIN"), tls_verify=True, auth_type="normal"
        )

        # Authenticate the TaigaBot account
        taigabot.auth(
            username=environ.get("TAIGABOT_ACCOUNT"),
            password=environ.get("TAIGABOT_PASSWORD"),
        )
    except TaigaException as exception:
        print(exception)
        return "Unable to authenticate into Taiga", 500

    request_json = request.get_json(silent=True)
    parameters = ParametersHandler("user_stories")

    try:
        data = parameters.parse_payload(request_json)
    except TaigaException as exception:
        return str(exception), 400
    except FileNotFoundError as exception:
        return f"File '{exception.filename}' not found", 404

    try:
        # Build the User Story with the parsed data
        taigabot.build_user_story(data)
    except TaigaException as exception:
        return str(exception), 400

    return "User Story created", 200
