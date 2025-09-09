from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import arrow
import ics
import json


Lesson = Dict[str, Any]


def parse_json_timetable(filename: str, days_to_ignore: Iterable[int] | None = None) -> List[Lesson]:
    days_to_ignore = set(days_to_ignore or [])
    lessons: List[Lesson] = []

    with open(filename, 'r', encoding='utf-8') as timetable_file:
        data = json.load(timetable_file)

    rooms: Dict[int, str] = {room['Id']: room['Abbrev'] for room in data.get('Rooms', [])}
    subjects: Dict[int, str] = {subject['Id']: subject['Name'] for subject in data.get('Subjects', [])}
    teachers: Dict[int, str] = {teacher['Id']: teacher['Name'] for teacher in data.get('Teachers', [])}
    hours: Dict[int, Dict[str, str]] = {
        hour['Id']: {"start": hour['BeginTime'], "end": hour['EndTime']} for hour in data.get('Hours', [])
    }

    for day in data.get('Days', []):
        if day.get('DayOfWeek') in days_to_ignore:
            continue

        date = arrow.get(day['Date'])
        for atom in day.get('Atoms', []):
            hour_def = hours.get(atom['HourId'])
            if not hour_def:
                continue

            start_h, start_m = hour_def['start'].split(':')
            end_h, end_m = hour_def['end'].split(':')

            item: Lesson = {
                'start': date.replace(hour=int(start_h), minute=int(start_m)),
                'end': date.replace(hour=int(end_h), minute=int(end_m)),
                'location': rooms.get(atom.get('RoomId')) or '?',
                'subject': subjects.get(atom.get('SubjectId')) or '?',
                'teacher': teachers.get(atom.get('TeacherId')) or '?',
                'change': None,
            }

            change = atom.get('Change')
            if change:
                if change.get('ChangeType') == 'Canceled':
                    continue
                item['change'] = change.get('Description')

            lessons.append(item)

    return lessons


def create_ics(lessons: Iterable[Lesson], output_path: str | Path) -> None:
    cal = ics.Calendar()

    for lesson in lessons:
        event = ics.Event()
        subject = lesson.get('subject', '?')
        teacher = lesson.get('teacher', '')
        change = lesson.get('change')

        event.name = f"[Z] {lesson.get('location', '')} - {subject}" if change else f"{lesson.get('location', '')} - {subject}"
        event.description = f"{teacher} \n[Z] {change}" if change else teacher
        event.location = lesson.get('location', '')
        event.begin = lesson['start']
        event.end = lesson['end']

        cal.events.add(event)

    ics_path = Path(output_path)
    ics_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ics_path, 'w', encoding='utf-8') as f:
        f.writelines(cal.serialize_iter())
