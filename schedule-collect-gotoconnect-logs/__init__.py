import datetime
import logging
import csv
import os
import tempfile
import azure.functions as func
from ..shared_code.gotoconnect import GoToConnect
from ..shared_code.azstorage import AzureStorage

logger = logging.getLogger('app')

# Get # of days to collect logs for, defaults to 1
day_count = os.getenv("DAYS_TO_RETRIEVE")
if not day_count or day_count < 1:
    logger.info("Setting day_count to 1")
    day_count = 1
else:
    day_count = int(day_count)

# Get starting day, defaults to yesterday (-1)
start_day = os.getenv("START_DAY")
if not start_day or start_day > -1:
    logger.info("Setting start day to -1 (yesterday)")
    start_day = -1
else:
    start_day = int(start_day)

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

    # Create gotoconnect connection object
    gotoconnect = GoToConnect()     

    days = start_day
    while days > start_day - day_count:
        date = datetime.date.today() + datetime.timedelta(days=days)
        users = gotoconnect.get_users(date)
        logger.info(f"Retrieved user list for {str(date)}")

        activity_list = []
        for user in users:
            user_activity = gotoconnect.get_user_activity(user['userId'], date)
            for item in user_activity:
                item["user"] = user['userName']
                # Convert duration from milliseconds to HH:MM:SS format and drop
                # remaining milliseconds
                duration=datetime.timedelta(milliseconds=item['duration'])
                item['duration']=str(duration).split('.')[0]
                if item['queue']:
                    item['queue'] = item['queue']['name']
                item['callerName'] = item['caller']['name']
                item['callerNumber'] = item['caller']['number']
                item['calleeName'] = item['callee']['name']
                item['calleeNumber'] = item['callee']['number']

            activity_list += user_activity
        logger.info(f"Retrieved all user activity for {str(date)}")

        # Write data to CSV file
        filename =  str(date) + "_jive_call_logs.csv"
        base_path = tempfile.gettempdir()
        path_to_file = os.path.join(base_path, filename)
        with open(path_to_file, 'w', newline='') as outfile:
            fields = ['user','queue','direction','disposition',
                        'startTime','endTime','answerTime','duration',
                        'callerName','callerNumber','calleeName','calleeNumber'
                    ]
            # Configure dictionary writer to ignore extra fields in the input data
            writer = csv.DictWriter(outfile, fieldnames=fields, extrasaction='ignore')    

            writer.writeheader()
            writer.writerows(activity_list)
        logger.info(f"CSV file {filename} created")
        
        # Write CSV file to Azure Storage in paths separated by year and month
        storage = AzureStorage()
        path = f"{date.year}/{date.month:02d}/"
        storage.write_file(path_to_file, path)
        logger.info(f"CSV file {filename} uploaded")

        # Remove CSV file from local storage
        os.remove(path_to_file)

        days += -1

