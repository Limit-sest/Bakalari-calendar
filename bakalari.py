from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional, Tuple

import requests


def get_token(
    school: str,
    username: str,
    password: str,
    refresh_token: Optional[str] = None,
) -> Tuple[str, str]:
    url = f"{school}/api/login"
    head = {"Content-Type": "application/x-www-form-urlencoded"}

    if refresh_token:
        body = f"client_id=ANDR&grant_type=refresh_token&refresh_token={refresh_token}"
        print("Getting tokens using refresh token")
    else:
        body = f"client_id=ANDR&grant_type=password&username={username}&password={password}"
        print("Getting tokens using username and password")

    response = requests.post(url, data=body, headers=head)

    # Fallback to username/password if refresh token invalid/expired
    if response.status_code == 400 and response.json().get("error_description") == "The specified token is invalid.":
        body = f"client_id=ANDR&grant_type=password&username={username}&password={password}"
        print("Refresh token invalid, retrying with username and password")
        response = requests.post(url, data=body, headers=head)

    if response.status_code == 200:
        print("Obtained new pair of tokens")
        data = response.json()
        return data["access_token"], data["refresh_token"]

    # Raise a clear error for callers to handle
    raise RuntimeError(response.json().get("error_description", f"Login failed: {response.status_code}"))


def get_timetable(school: str, token: str, future: bool = False) -> Optional[str]:
    if future:
        url = f"{school}/api/3/timetable/actual?date={(date.today() + timedelta(weeks=1)).strftime('%Y-%m-%d')}"
        filename = "timetable_future.json"
    else:
        url = f"{school}/api/3/timetable/actual?date={date.today().strftime('%Y-%m-%d')}"
        filename = "timetable.json"

    head = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=head)
    if response.status_code == 200:
        with open(filename, 'w', encoding='utf-8') as timetable:
            json.dump(response.json(), timetable, indent=4, ensure_ascii=False)
        return None
    if response.status_code == 401:
        return "401 Error"
    raise RuntimeError(f"Failed to fetch timetable: {response.status_code}")
