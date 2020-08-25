import datetime
import logging
import csv
import os
import azure.functions as func
from ..shared_code.gotoconnect_api import refresh_access_token, get_jive_users, get_jive_user_activity
from ..shared_code.azstorage import AzureStorage

logger = logging.getLogger('app')

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

    token = refresh_access_token()
    logger.info("retrieved token")
    users = get_jive_users(token)
    logger.info("retrieved user list")

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
    logger.info("retrieved all user activity")

    date = datetime.date.today() + datetime.timedelta(days=-1)
  
    filename =  str(date) + "_jive_call_logs.csv"
    path_to_file = os.path.join(os.getcwd(), filename)
    with open(filename, 'w', newline='') as outfile:
        fields = ['user','queue','direction','disposition','startTime','endTime','answerTime','duration',]
        # Configure dictionary writer to ignore extra fields in the input data
        writer = csv.DictWriter(outfile, fieldnames=fields, extrasaction='ignore')    

        writer.writeheader()
        writer.writerows(activity_list)
    logger.info("csv file created")
    
    storage = AzureStorage()

    path = f"{date.year}/{date.month}/"
    storage.write_file(path_to_file, path)

    logger.info("csv file uploaded")

