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

    if request.method != 'POST':
        return f"Invalid method {request.method}", 405

    taiga_domain = environ.get("TAIGA_DOMAIN")
    taigabot_account = environ.get("TAIGABOT_ACCOUNT")
    taigabot_password = environ.get("TAIGABOT_PASSWORD")

    if None in [taiga_domain, taigabot_account, taigabot_password]:
        return "Unable to retrieve credentials for Taigabot", 403

    try:
        # Initialize the bot
        taigabot = TaigaBot(
            host=taiga_domain, tls_verify=True, auth_type="normal"
        )

        # Authenticate the TaigaBot account
        taigabot.auth(
            username=taigabot_account,
            password=taigabot_password,
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
    except PermissionError as exception:
        return f"Permission error on file '{exception.filename}'", 403

    try:
        # Build the User Story with the parsed data
        taigabot.build_user_story(data)
    except TaigaException as exception:
        return str(exception), 400

    return "User Story created", 200
