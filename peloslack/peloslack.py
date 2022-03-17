
from datetime import datetime, timedelta
import os


import pylotoncycle
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from timeloop import Timeloop


username = os.environ['PTON_USERNAME']
password = os.environ['PTON_PASSWORD']
slack_bot_token = os.environ['SLACK_BOT_TOKEN']
conn = pylotoncycle.PylotonCycle(username, password)
last_start_time = "1615617614"
last_end_time = "1615617614"
tl = Timeloop()
slack_client = WebClient(token=slack_bot_token)


WORKOUT_TO_EMOJI_AND_STATUS = {
    'yoga': {
        'emoji': ':person_in_lotus_position:',
        'message': 'Namaste',
    },
    'stretching': {
        'emoji': ':man-gesturing-ok:',
        'message': 'Stretch',
    },
    'meditation': {
        'emoji': ':person_in_lotus_position:',
        'message': 'Meditating',
    },
    'stretching': {
        'emoji': ':person_in_lotus_position:',
        'message': 'Namaste',
    },
    'running': {
        'emoji': ':man-running:',
        'message': 'Out for a run',
    }
}


def set_slack_status(workout):
    global last_start_time

    start_time = str(workout["start_time"])

    if last_start_time == start_time:
        return

    last_start_time = start_time
    workout_title = str(workout["ride"]["title"])
    instructor = str(workout["instructor_name"])

    try:
        status = WORKOUT_TO_EMOJI_AND_STATUS[workout["fitness_discipline"]]
    except KeyError:
        status = {
            'emoji': ':man-biking:',
            'message': 'Riding the Peloton',
        }
    status_emoji = status['emoji']
    status_message = status['message']

    status_message += ": "
    status_message += workout_title
    status_message += " w/ "
    status_message += instructor

    print(f"Setting profile with message={status_message}, emoji={status_emoji}")

    slack_client.api_call(
        api_method = 'users.profile.set',
        json = {
            "profile": {
                "status_text": status_message,
                "status_emoji": status_emoji
            }
        }
    )


def clear_slack_status(workout):
    global last_end_time

    end_time = str(workout["end_time"])

    if last_end_time == end_time:
        return

    last_end_time = end_time

    print("Clearing Slack status")

    slack_client.api_call(
        api_method = 'users.profile.set',
        json = {
            "profile": {
                "status_text": "",
                "status_emoji": ""
            }
        }
    )


@tl.job(interval=timedelta(seconds=60))
def mainloop():
    try:
        workout = conn.GetRecentWorkouts(1)[0]
        status = workout["status"]
        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")
        print(f"Time: {now_str}. Status: {status}")

        if (status == 'COMPLETE'):
            clear_slack_status(workout)
        elif (status == 'IN_PROGRESS'):
            set_slack_status(workout)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    tl.start(block=True)
