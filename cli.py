import bakalari
import timetable_cal
import yaml
import click

school_url, username, password, access_token, refresh_token = (None, None, None, None, None)

def refresh_tokens(s_url=None, user=None, pwd=None):
    global school_url, username, password, access_token, refresh_token

    # Use provided args or fall back to globals
    school_url = s_url or school_url
    username = user or username
    password = pwd or password

    access_token, refresh_token = bakalari.get_token(school_url, username, password, refresh_token)

@click.command()
@click.argument('s_url', type=str, required=True)
@click.argument('user', type=str, required=True)
@click.argument('pwd', type=str, required=True)
def main(s_url, user, pwd):
    global school_url, username, password
    school_url, username, password = s_url, user, pwd

    with open('config.yml', 'r') as config_file:
        config = yaml.safe_load(config_file)
    if bakalari.get_timetable(school_url, access_token) == "401 Error":
        refresh_tokens(school_url, username, password)
        bakalari.get_timetable(school_url, access_token)

    if config['download_future']:
        if bakalari.get_timetable(school_url, access_token, True) == "401 Error":
            refresh_tokens()
            bakalari.get_timetable(school_url, access_token, True)

    timetable_cal.parse_json_timetable('timetable.json')
    if config['download_future']:
        timetable_cal.parse_json_timetable('timetable_future.json')

    timetable_cal.create_ics()

if __name__ == '__main__':
    main()
