
from datetime import datetime, timedelta
import os


import pylotoncycle
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from timeloop import Timeloop

from dotenv import load_dotenv
load_dotenv()


username = os.environ['PTON_USERNAME']
password = os.environ['PTON_PASSWORD']
slack_bot_token = os.environ['SLACK_BOT_TOKEN']
conn = pylotoncycle.PylotonCycle(username, password)
last_start_time = "1615617614"
tl = Timeloop()
slack_client = WebClient(token=slack_bot_token)


WORKOUT_TO_EMOJI_AND_STATUS = {
    'yoga': {
        'emoji': ':person_in_lotus_position:',
        'message': 'Namaste',
    },
    'stretching': {
        'emoji': ':person_in_lotus_position:',
        'message': 'Namaste',
    },
    'running': {
        'emoji': ':man-running:',
        'status_message': 'Out for a run',
    }
}


def set_slack_status(workout):
    global last_start_time

    start_time = str(workout["start_time"])  # e.g.: 1615617614

    if last_start_time == start_time:
        return

    last_start_time = start_time
    end_time = str(workout["end_time"])  # e.g.: 1615618814
    workout_title = str(workout["ride"]["title"])
    instructor = str(workout["instructor_name"])

    try:
        status = WORKOUT_TO_EMOJI_AND_STATUS[workout["fitness_discipline"]]
    except KeyError:
        status = {
            'emoji': ':man-biking:',
            'status_message': 'Riding the Peloton',
        }
    status_emoji = status['emoji']
    status_message = status['message']

    status_message += ": "
    status_message += workout_title
    status_message += " w/ "
    status_message += instructor

    print(f"Setting profile with message={status_message}, emoji={status_emoji}, exp={end_time}")

    slack_client.api_call(
        api_method = 'users.profile.set',
        json = {
            "profile": {
                "status_text": status_message,
                "status_emoji": status_emoji,
                "status_expiration": end_time
            }
        }
    )


def poll_and_set_slack():
    workout = conn.GetRecentWorkouts(1)[0]
    status = workout["status"]

    if (status == 'COMPLETE'):
        print("Status: Complete")
    elif (status == 'IN_PROGRESS'):
        print("Status: In Progress")
        set_slack_status(workout)
    else:
        print(f"Status: {status}")


@tl.job(interval=timedelta(seconds=30))
def mainloop():
    poll_and_set_slack()


if __name__ == "__main__":
    tl.start(block=True)
