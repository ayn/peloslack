import pylotoncycle
import os
from timeloop import Timeloop
from datetime import datetime
from datetime import timedelta
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

username = os.environ['PTON_USERNAME']
password = os.environ['PTON_PASSWORD']
slack_bot_token = os.environ['SLACK_BOT_TOKEN']
conn = pylotoncycle.PylotonCycle(username, password)
status_updated = False
tl = Timeloop()
slack_client = WebClient(token=slack_bot_token)

def set_slack_status(workout):
    global status_updated
    global conn

    if status_updated:
        return

    # print(workout)
    start_time = str(workout["start_time"]) # e.g.: 1615617614
    end_time = str(workout["end_time"]) # e.g.: 1615618814
    workout_title = str(workout["ride"]["title"])
    instructor = str(workout["instructor_name"])

    status_updated = True

    status_emoji = ":man-biking:"
    status_message = "Riding the Peloton"

    if (workout["fitness_discipline"] == "yoga" or workout["fitness_discipline"] == "stretching"):
        status_emoji = ":person_in_lotus_position:"
        status_message = "Namaste"
    elif (workout["fitness_discipline"] == "running"):
        status_emoji = ":man-running:"
        status_message = "Out for a run"

    status_message += ": "
    status_message += workout_title
    status_message += " w/ "
    status_message += instructor

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

@tl.job(interval=timedelta(seconds=30))
def mainloop():
    workout = conn.GetRecentWorkouts(1)[0]
    state = workout["status"]

    if (workout["status"] == 'COMPLETE'):
        print("Status: Complete")
        print(workout)
        status_updated = False
    elif (workout["status"] == 'IN_PROGRESS'):
        print("Status: In Progress")
        set_slack_status(workout)
    else:
        print("Unknown")

if __name__ == "__main__":
    tl.start(block=True)
