import json
import ics
import arrow
import yaml
from pathlib import Path

# Format: [{subject:"Math", location:"Room 123", start:"", end:"", teacher:"", changes:""/None}, {...}, ...]
timetable = []


def parse_json_timetable(filename: str):
    global timetable
    timetable = []

    with open(filename, 'r') as timetable_file:
        rooms = {}
        subjects = {}
        teachers = {}
        hours = {}
        timetable_json = json.load(timetable_file)

        for room in timetable_json['Rooms']:
            rooms[room['Id']] = room['Abbrev']

        for subject in timetable_json['Subjects']:
            subjects[subject['Id']] = subject['Name']

        for teacher in timetable_json['Teachers']:
            teachers[teacher['Id']] = teacher['Name']

        for hour in timetable_json['Hours']:
            hours[hour['Id']] = {"start": hour['BeginTime'], "end": hour['EndTime']}

        for day in timetable_json['Days']:
            date = arrow.get(day['Date'])
            for lesson in day['Atoms']:
                start_h, start_m = hours[lesson['HourId']]['start'].split(':')
                end_h, end_m = hours[lesson['HourId']]['end'].split(':')

                obj = {
                    'start': date.replace(hour=int(start_h), minute=int(start_m)),
                    'end': date.replace(hour=int(end_h), minute=int(end_m))
                }

                if lesson['RoomId'] is None:
                    obj['location'] = '?'
                else:
                    obj['location'] = rooms[lesson['RoomId']]

                if lesson['SubjectId'] is None:
                    obj['subject'] = '?'
                else:
                    obj['subject'] = subjects[lesson['SubjectId']]

                if lesson['TeacherId'] is None:
                    obj['teacher'] = '?'
                else:
                    obj['teacher'] = teachers[lesson['TeacherId']]

                if lesson['Change']:
                    if lesson['Change']['ChangeType'] == "Canceled":
                        continue
                    else:
                        obj['change'] = lesson['Change']['Description']
                else:
                    obj['change'] = None

                timetable.append(obj)


def create_ics():
    global timetable

    c = ics.Calendar()

    for lesson in timetable:
        e = ics.Event()
        e.name = lesson['subject']
        if lesson['change']:
            e.description = f"{lesson['teacher']} \n!ZMĚNA: {lesson['change']}"
        else:
            e.description = lesson['teacher']
        e.location = lesson['location']
        e.end = lesson['end']
        e.begin = lesson['start']

        c.events.add(e)

    with open('config.yml', 'r') as config_file:
        config = yaml.safe_load(config_file)

    ics_path = Path(config['path'])
    ics_path.parent.mkdir(parents=True, exist_ok=True)

    with open(ics_path, 'w', encoding='utf-8') as f:
        f.writelines(c.serialize_iter())
