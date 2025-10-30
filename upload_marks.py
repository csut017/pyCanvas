import argparse
import math
import numpy as np
import pandas as pd
from canvas import Canvas

def _retrieve_value(map, name):
    try:
        value = map[name]
        if str(value) == 'nan':
            value = None
    except KeyError:
        value = None
    return value

def main():
    parser = argparse.ArgumentParser(
        prog = 'upload_marks.py',
        description = 'This utility will download all the marks for an assignment from Canvas.'
    )
    parser.add_argument('course', help = 'The identifier of the course')
    parser.add_argument('assignment', help = 'The identifier of the assignment')
    parser.add_argument('file_path', help = 'The path to the file to download the marks to')
    parser.add_argument('--rubrics', action = 'store_true', help = 'Include the rubric scores')
    args = parser.parse_args()

    conn = Canvas('https://canvas.auckland.ac.nz')
    print('Starting Canvas mark upload')
    current_user = conn.get_current_user()
    print('Current user is ' + current_user['name'])

    course = conn.get_course(args.course)
    print('Course name is ' + course['name'])

    assignment = conn.get_assignment(args.course, args.assignment)
    print('Assignment name is ' + assignment['name'])
    mapping = {}
    if args.rubrics:
        for item in assignment['rubric']:
            mapping[item['description']] = item
            item['ratings_map'] = { item['points']: item['id'] for item in item['ratings'] }

    print('Retrieving students...')
    student_list = conn.list_students_in_course(args.course)
    print(f'...done, retrieved {len(student_list)} students')
    students_by_upi = { student['login_id']: student['id'] for student in student_list }
    students_by_auid = { student['sis_user_id']: student['id'] for student in student_list }

    print('Reading Excel file')
    df = pd.read_excel(args.file_path)
    for index, row in df.iterrows():
        index += 2
        try:
            name = row['Name']
        except KeyError:
            print(f'Missing name for row {index} - cannot process')
            continue

        upi = _retrieve_value(row, 'UPI')
        auid = _retrieve_value(row, 'AUID')

        if upi is None and auid is None:
            print(f'Missing UPI and AUID for row {index} - cannot process')
            continue

        print(f'Processing row {index}: {name} [{upi}]')
        try:
            student = students_by_upi[upi]
        except KeyError:
            try:
                student = students_by_auid[auid]
            except KeyError:
                print(f'Unknown student at row {index} ({name}) - cannot process')
                continue

        mark = _retrieve_value(row, 'Mark')
        comment = _retrieve_value(row, 'Comment')
        rubric = None

        if args.rubrics:
            rubric = {}
            for key, item in mapping.items():
                value = _retrieve_value(row, key)
                if value is None:
                    continue
                item_value = {
                    'points': value
                }
                rubric[item['id']] = item_value

                try:
                    rating = item['ratings_map'][value]
                    item_value['rating_id'] = rating
                except KeyError:
                    pass

            if len(rubric) == 0:
                rubric = None

        rsp = conn.mark_submission(
            args.course, 
            args.assignment, 
            student, 
            mark, 
            comment,
            rubric)
        print(rsp)

if __name__ == '__main__':
    main()
