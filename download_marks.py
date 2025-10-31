import argparse
import pandas as pd
from canvas import Canvas, Parameters

def main():
    parser = argparse.ArgumentParser(
        prog = 'download_marks.py',
        description = 'This utility will download all the marks for an assignment from Canvas.'
    )
    parser.add_argument('course', help = 'The identifier of the course')
    parser.add_argument('assignment', help = 'The identifier of the assignment')
    parser.add_argument('file_path', help = 'The path to the file to download the marks to')
    parser.add_argument('--rubrics', action = 'store_true', help = 'Include the rubric scores')
    parser.add_argument('--comments', action = 'store_true', help = 'Include the comments')
    args = parser.parse_args()

    conn = Canvas('https://canvas.auckland.ac.nz')
    print('Starting Canvas mark download')
    current_user = conn.get_current_user()
    print('Current user is ' + current_user['name'])

    course = conn.get_course(args.course)
    print('Course name is ' + course['name'])

    assignment = conn.get_assignment(args.course, args.assignment)
    print('Assignment name is ' + assignment['name'])

    print('Retrieving submissions...')
    params = Parameters()
    params.add('include[]', 'user')
    if args.rubrics:
        params.add('include[]', 'rubric_assessment')
    if args.comments:
        params.add('include[]', 'submission_comments')
    params.add('per_page', '50')
    submissions = conn.list_submissions(args.course, args.assignment, params)
    data = {'Name': [], 'UPI': [], 'AUID': [], 'Mark': []}
    mapping = {}
    if args.rubrics:
        for item in assignment['rubric']:
            mapping[item['id']] = item['description']
            data[item['description']] = []
    if args.comments:
        data['Comments'] = []
    for submission in submissions:
        data['Name'].append(submission['user']['name'])
        data['UPI'].append(submission['user']['login_id'])
        data['AUID'].append(submission['user']['sis_user_id'])
        data['Mark'].append(submission['score'])
        if args.rubrics:
            try:
                rubric = submission['rubric_assessment']
            except KeyError:
                rubric = None
            
            if rubric is None:
                for _, item in mapping.items():
                    data[item].append(None)
            else:
                for key, item in mapping.items():
                    existing = data[item]
                    try:
                        existing.append(rubric[key]['points'])
                    except KeyError:
                        existing.append(None)

        if args.comments:
            data['Comments'].append('\n'.join([comment['comment'] for comment in submission['submission_comments']]))
    df = pd.DataFrame(data)
    print('...done')
    df.to_excel(args.file_path, sheet_name = 'Marks', index = False)
    print('Saved to ' + args.file_path)

if __name__ == '__main__':
    main()
