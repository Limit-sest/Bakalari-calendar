from __future__ import annotations

import os
import re
import sys
from typing import Tuple

import yaml
from dotenv import load_dotenv, set_key

import bakalari
from timetable_cal import create_ics, parse_json_timetable


def load_or_prompt_credentials() -> Tuple[str, str, str, str | None, str | None]:
    if os.path.isfile('.env'):
        load_dotenv('.env')
        school_url = os.getenv('SCHOOL_URL', '')
        username = os.getenv('USERNAME', '')
        password = os.getenv('PASSWORD', '')
        access_token = os.getenv('ACCESS_TOKEN')
        refresh_token = os.getenv('REFRESH_TOKEN')

        # If tokens are missing but credentials exist, fetch and persist them.
        if school_url and username and password and (not access_token or not refresh_token):
            try:
                access_token, refresh_token = bakalari.get_token(school_url, username, password)
            except RuntimeError as e:
                print(f"Login failed: {e}")
                sys.exit(1)
            set_key('.env', 'ACCESS_TOKEN', access_token)
            set_key('.env', 'REFRESH_TOKEN', refresh_token)

        return (school_url, username, password, access_token, refresh_token)

    school_url = input(
        'Prosím zadej URL své školy - Pokud je přihlášení do Bakalářů na adrese '
        'https://www.example.com/next/login.aspx, pak bude požadovaná adresa https://www.example.com: '
    ).strip('/')
    if not re.match(r'(?:http[s]?://.)?(?:www\.)?[-a-zA-Z0-9@%._+~#=]{2,256}\.[a-z]{2,6}\b(?:[-a-zA-Z0-9@:%_+.~#?&//=]*)', school_url):
        sys.exit('Zadej URL adresu ve správném formátu!')

    username = input('Prosím zadej své uživ. jméno: ')
    password = input('Prosím zadej své heslo: ')
    try:
        access_token, refresh_token = bakalari.get_token(school_url, username, password)
    except RuntimeError as e:
        print(f"Login failed: {e}")
        sys.exit(1)

    with open('.env', 'w', encoding='utf-8') as f:
        f.write(f'SCHOOL_URL={school_url}\n')
        f.write(f'ACCESS_TOKEN={access_token}\n')
        f.write(f'REFRESH_TOKEN={refresh_token}\n')
        f.write(f'USERNAME={username}\n')
        f.write(f'PASSWORD={password}\n')

    return school_url, username, password, access_token, refresh_token


def refresh_tokens(school_url: str, username: str, password: str, refresh_token: str | None) -> Tuple[str, str]:
    access_token, refresh_token = bakalari.get_token(school_url, username, password, refresh_token)
    set_key('.env', 'ACCESS_TOKEN', access_token)
    set_key('.env', 'REFRESH_TOKEN', refresh_token)
    return access_token, refresh_token


def main() -> None:
    with open('config.yml', 'r', encoding='utf-8') as config_file:
        config = yaml.safe_load(config_file)

    school_url, username, password, access_token, refresh_token = load_or_prompt_credentials()

    access_token = access_token or ''
    if bakalari.get_timetable(school_url, access_token) == '401 Error':
        access_token, refresh_token = refresh_tokens(school_url, username, password, refresh_token)
        bakalari.get_timetable(school_url, access_token)

    if config.get('download_future'):
        if bakalari.get_timetable(school_url, access_token or '', True) == '401 Error':
            access_token, refresh_token = refresh_tokens(school_url, username, password, refresh_token)
            bakalari.get_timetable(school_url, access_token, True)

    lessons = parse_json_timetable('timetable.json', config.get('days_to_ignore'))
    if config.get('download_future'):
        lessons += parse_json_timetable('timetable_future.json', config.get('days_to_ignore'))

    create_ics(lessons, config.get('path', './timetable.ics'))


if __name__ == '__main__':
    main()
