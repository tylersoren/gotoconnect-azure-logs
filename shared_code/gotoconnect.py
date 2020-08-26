import os
import requests
import base64
import logging
from datetime import date, datetime, timedelta

logger = logging.getLogger('app')

refresh_token = os.getenv("GOTOCONNECT_REFRESH_TOKEN")
if not refresh_token:
    raise ValueError("Need to define GOTOCONNECT_REFRESH_TOKEN environment variable")

client_id = os.getenv("GOTOCONNECT_CLIENT_ID")
if not refresh_token:
    raise ValueError("Need to define GOTOCONNECT_CLIENT_ID environment variable")

client_secret = os.getenv("GOTOCONNECT_CLIENT_SECRET")
if not refresh_token:
    raise ValueError("Need to define GOTOCONNECT_CLIENT_SECRET environment variable")

def get_auth_url(client_id):
  return f"https://authentication.logmeininc.com/oauth/authorize?client_id={client_id}&response_type=code"

# Get date time at beginning of day 00:00:00
# return string in ISO 8601 format along with URL char formatting
def _day_start(date):
  start = datetime.combine(date, datetime.min.time()).isoformat().replace(":","%3A")
  return start

# Get date time at end of day 23:59:59
# return string in ISO 8601 format along with URL char formatting
def _day_end(date):
  end = datetime.combine(date, datetime.max.time()).replace(microsecond=0).isoformat().replace(":","%3A")
  return end


# Take a string as input and return a base64 encoded string
def _base64_encode(text):
  text_bytes = text.encode('ascii')
  encoded_bytes = base64.b64encode(text_bytes)
  encoded_string = encoded_bytes.decode('ascii')
  
  return encoded_string

class GoToConnect:
  def __init__(self):
    self.access_token = None
    self.token_expiration = datetime.now()
    self.principal = ""
    self.refresh_access_token()
        
  def get_access_token(self, authorization_code, client_id=client_id, client_secret=client_secret):
    basic_auth = f"{client_id}:{client_secret}"
    basic_auth = base64.b64encode(basic_auth.encode('ascii'))

    url = "https://authentication.logmeininc.com/oauth/token" 
    headers = { 'Accept': 'application/json', 
      'Content-Type': 'application/x-www-form-urlencoded', 
      'Authorization': f'Basic {basic_auth}' }
    body =  "grant_type=authorization_code&code=$authorizationCode"
    
    response = requests.post(url, data=body, headers=headers)

    return response.json()

  def refresh_access_token(self, refresh_token=refresh_token, client_id=client_id, client_secret=client_secret):
    encoded_auth = _base64_encode(f"{client_id}:{client_secret}")

    url = "https://authentication.logmeininc.com/oauth/token" 
    headers = { 'Accept': 'application/json', 
      'Content-Type': 'application/x-www-form-urlencoded', 
      'Authorization': f'Basic {encoded_auth}' }
    body =  f"grant_type=refresh_token&refresh_token={refresh_token}"
    
    response = requests.post(url, data=body, headers=headers)

    # Set token and add expiration in seconds to current time
    self.access_token = response.json()['access_token']
    self.token_expiration = datetime.now() + timedelta(seconds=response.json()['expires_in']) 
    self.principal = response.json()['principal']

    logger.info(f"Token refreshed for principal {self.principal} and expires {self.token_expiration}")

  
  # Check if token is expired and refresh if needed
  def check_token_expiry(self):
    if datetime.now() > self.token_expiration:
      logger.info("Access token is expired. Refreshing token...")
      self.refresh_access_token()
      

  def get_users(self, date):
    self.check_token_expiry()

    headers = { 'Accept': 'application/json',
      'Authorization': f'Bearer {self.access_token}' }

    start = _day_start(date)
    end = _day_end(date)
    url = f"https://api.jive.com/call-reports/v1/reports/user-activity?startTime={start}&endTime={end}"
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
      logger.error('Failed to pull User Summary')
      return None
    return response.json()['items']


  def get_user_activity(self, user_id, date):
    self.check_token_expiry()

    start = _day_start(date)
    end = _day_end(date)

    headers = { 'Accept': 'application/json',
      'Authorization': f'Bearer {self.access_token}' }
    url = f"https://api.jive.com/call-reports/v1/reports/user-activity/{user_id}?startTime={start}&endTime={end}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
      logger.error(f'Failed to pull User Activity for {user_id}')

    return response.json()['items']
