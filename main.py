import functions_framework
from os import environ

from commons import TaigaException
from parameters_handler import ParametersHandler
from taiga_bot import TaigaBot


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
           password=environ.get("TAIGABOT_PASSWORD")
        )
    except TaigaException as e:
        print(e)
        return f"Unable to authenticate into Taiga", 500

    request_json = request.get_json(silent=True)
    parameters = ParametersHandler("user_stories")

    try:
        data = parameters.parse_payload(request_json)
    except TaigaException as e:
        return str(e), 400
    except FileNotFoundError as e:
        return f"File '{e.filename}' not found", 404

    try:
        # Parse the file received and build its User Story
        # user_story = taigabot.parse_user_story_from_json(filename)
        # user_story = merge_data_into_user_story(user_story, data)
        print(data)

        taigabot.build_user_story(data)
    except TaigaException as e:
        return str(e), 400

    return 'User Story created', 200
