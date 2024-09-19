import sys
import bakalari
import calendar
import re
from dotenv import set_key, load_dotenv
import os
from time import sleep

school_url, username, password, access_token, refresh_token = (None, None, None, None, None)


def first_login():
    global school_url, username, password, access_token, refresh_token

    # Load/create configuration
    if os.path.isfile(".env"):
        load_dotenv(".env")

        school_url = os.getenv("SCHOOL_URL")
        access_token = os.getenv("ACCESS_TOKEN")
        refresh_token = os.getenv("REFRESH_TOKEN")
        username = os.getenv("USERNAME")
        password = os.getenv("PASSWORD")
    else:
        school_url = input("Prosím zadej URL své školy - Pokud je přihlášení do Bakalářů na adrese "
                           "https://www.example.com/next/login.aspx, pak bude požadovaná adresa "
                           "https://www.example.com: ").strip("/")

        if re.match(
                r"(?:http[s]?:\/\/.)?(?:www\.)?[-a-zA-Z0-9@%._\+~#=]{2,256}\.[a-z]{2,6}\b(?:[-a-zA-Z0-9@:%_\+.~#?&\/\/=]*)",
                school_url):
            pass
        else:
            sys.exit("Zadej URL adresu ve správném formátu!")

        username = input("Prosím zadej své uživ. jméno: ")
        password = input("Prosím zadej své heslo: ")
        access_token, refresh_token = bakalari.get_token(school_url, username, password)

        with open(".env", "w") as f:
            f.write(f"SCHOOL_URL={school_url}\n")
            f.write(f"ACCESS_TOKEN={access_token}\n")
            f.write(f"REFRESH_TOKEN={refresh_token}\n")
            f.write(f"USERNAME={username}\n")
            f.write(f"PASSWORD={password}\n")
            f.close()

def refresh_tokens():
    global school_url, username, password, access_token, refresh_token

    access_token, refresh_token = bakalari.get_token(school_url, username, password, refresh_token)
    set_key(".env", "ACCESS_TOKEN", access_token)
    set_key(".env", "REFRESH_TOKEN", refresh_token)

def main():
    global school_url, username, password, access_token, refresh_token

    first_login()

    while True:
        if bakalari.get_timetable(school_url, access_token) == "401 Error":
            refresh_tokens()
            bakalari.get_timetable(school_url, access_token)
        sleep(10 * 60)


if __name__ == '__main__':
    main()
