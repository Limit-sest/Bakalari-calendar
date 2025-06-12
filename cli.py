import bakalari
import timetable_cal
import yaml
import click

school_url, username, password, access_token, refresh_token = (None, None, None, None, None)

def refresh_tokens():
    global school_url, username, password, access_token, refresh_token

    access_token, refresh_token = bakalari.get_token(school_url, username, password, refresh_token)

@click.command()
@click.argument('school_url', type=str, required=False)
@click.argument('username', type=str, required=False)
@click.argument('password', type=str, required=False)
def main():
    with open('config.yml', 'r') as config_file:
        config = yaml.safe_load(config_file)
    if bakalari.get_timetable(school_url, access_token) == "401 Error":
        refresh_tokens()
        bakalari.get_timetable(school_url, access_token)

    if config['download_future']:
        if bakalari.get_timetable(school_url, access_token, True) == "401 Error":
            refresh_tokens()
            bakalari.get_timetable(school_url, access_token, True)

    timetable_cal.parse_json_timetable('timetable.json')
    if config['download_future']:
        timetable_cal.parse_json_timetable('timetable_future.json')

    timetable_cal.create_ics()
