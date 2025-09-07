import click
import yaml

import bakalari
from timetable_cal import create_ics, parse_json_timetable


def ensure_access_token(school_url: str, username: str, password: str, access_token: str | None, refresh_token: str | None):
    if not school_url or not username or not password:
        raise RuntimeError('Missing school URL, username or password')
    if not access_token or not refresh_token:
        return bakalari.get_token(school_url, username, password)
    return access_token, refresh_token


@click.command()
@click.argument('s_url', type=str, required=True)
@click.argument('user', type=str, required=True)
@click.argument('pwd', type=str, required=True)
def main(s_url: str = '', user: str = '', pwd: str = '') -> None:
    with open('config.yml', 'r', encoding='utf-8') as config_file:
        config = yaml.safe_load(config_file)

    access_token: str | None = None
    refresh_token: str | None = None
    access_token, refresh_token = ensure_access_token(s_url, user, pwd, access_token, refresh_token)

    if bakalari.get_timetable(s_url, access_token) == "401 Error":
        access_token, refresh_token = bakalari.get_token(s_url, user, pwd, refresh_token)
        bakalari.get_timetable(s_url, access_token)

    if config.get('download_future'):
        if bakalari.get_timetable(s_url, access_token, True) == "401 Error":
            access_token, refresh_token = bakalari.get_token(s_url, user, pwd, refresh_token)
            bakalari.get_timetable(s_url, access_token, True)

    lessons = parse_json_timetable('timetable.json', config.get('days_to_ignore'))
    if config.get('download_future'):
        lessons += parse_json_timetable('timetable_future.json', config.get('days_to_ignore'))

    create_ics(lessons, config.get('path', './timetable.ics'))


if __name__ == '__main__':
    main()
