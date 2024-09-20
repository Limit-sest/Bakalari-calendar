import json
import ics
import arrow

timetable = [] # Format: [{subject:"Math", location:"Room 123", start:"", end:"", teacher:"", changes:""/None}, {...}, ...]

def parse_json_timetable():
    global timetable

    with open('timetable.json', 'r') as timetable_file:
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
                start_h, start_m = hours[lesson['HourID']]['start'].split(':')
                end_h, end_m = hours[lesson['HourID']]['end'].split(':')
                obj = {
                    'location': rooms[lesson['RoomId']],
                    'subject': subjects[lesson['SubjectId']],
                    'teacher': teachers[lesson['TeacherId']],
                    'start': date.replace(hour=start_h, minute=start_m),
                    'end': date.replace(hour=end_h, minute=end_m)
                }

                if lesson['Change']:
                    obj['change'] = lesson['Change']['Description']
                else:
                    obj['change'] = None

                timetable.append(obj)


def create_ics():
    global timetable

    c = ics.Calendar()
    e = ics.Event()

    with open('timetable.ics', 'w') as f:
        f.writelines(c.serialize_iter())