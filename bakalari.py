import sys
import json
import requests
from datetime import date

def get_token(school, username, password, refresh_token=None):
    url = f'{school}/api/login'
    head = {'Content-Type': 'application/x-www-form-urlencoded'}

    if refresh_token:
        body = f"client_id=ANDR&grant_type=refresh_token&refresh_token={refresh_token}"
        print("Getting tokens using refresh token")
    else:
        body = f'client_id=ANDR&grant_type=password&username={username}&password={password}'
        print("Getting tokens using username and password")

    response = requests.post(url, data=body, headers=head)

    # Use username and password if refresh token is expired/invalid
    if response.status_code == 400 and response.json()["error_description"] == "The specified token is invalid.":
        body = f'client_id=ANDR&grant_type=password&username={username}&password={password}'
        print("Getting tokens using refresh token")
        response = requests.post(url, data=body, headers=head)

    if response.status_code == 200:
        print("Obtained new pair of tokens")
        return response.json()['access_token'], response.json()['refresh_token']
    else:
        sys.exit(response.json()['error_description'])

def get_timetable(school, token):
    url = f'{school}/api/3/timetable/actual?date={date.today().strftime("%Y-%m-%d")}'
    head = {'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': f'Bearer {token}'}

    response = requests.get(url, headers=head)
    if response.status_code == 200:
        with open('timetable.json', 'w') as timetable:
            json.dump(response.json(), timetable, indent=4)
    elif response.status_code == 401:
        return "401 Error"