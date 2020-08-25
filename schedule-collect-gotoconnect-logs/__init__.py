import datetime
import logging
import csv


import azure.functions as func
from ..shared_code.gotoconnect_api import refresh_access_token, get_jive_users, get_jive_user_activity

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

    token = refresh_access_token()
    users = get_jive_users(token)

    activity_list = []
    for user in users:
        user_activity = get_jive_user_activity(user['userId'], token)
        for item in user_activity:
            item["user"] = user['userName']
            # Convert duration from milliseconds to HH:MM:SS format and drop
            # remaining milliseconds
            duration=datetime.timedelta(milliseconds=item['duration'])
            item['duration']=str(duration).split('.')[0]
            if item['queue']:
                item['queue'] = item['queue']['name']

        activity_list += user_activity
    filename = str(datetime.date.today()) + "_jive_call_logs.csv"
    with open(filename, 'w', newline='') as outfile:
        fields = ['user','queue','direction','disposition','startTime','endTime','answerTime','duration',]
        # Configure dictionary writer to ignore extra fields in the input data
        writer = csv.DictWriter(outfile, fieldnames=fields, extrasaction='ignore')    

        writer.writeheader()
        writer.writerows(activity_list)
