import keyring
import requests
from urllib.parse import quote_plus

class ParameterValue(object):
    def __init__(self, key, value):
        self.key = key
        self.value = value

def _split_link(link):
    parts = link.split(';')
    return (parts[1][6:-1], parts[0][1:-1])

class Parameters(object):
    def __init__(self):
        self._args = []

    def add(self, name, value):
        self._args.append(ParameterValue(name, value))

    def generate(self):
        if len(self._args) == 0:
            return ''
        items = [item.key + '=' + quote_plus(item.value) for item in self._args]
        return '&'.join(items)

class Canvas(object):
    def __init__(self, base_url):
        token = keyring.get_password('pyCanvas', 'token')
        self._base_url = base_url
        self._headers = {
            'Authorization': 'Bearer ' + token,
            'Accept': 'application/json'
        }

    def _get(self, url, parameters = None):
        full_url = self._base_url + url
        if not parameters is None:
            full_url += '?' + parameters.generate()

        rsp = requests.get(
            full_url, 
            headers = self._headers)
        rsp.raise_for_status()
        return rsp.json()
    
    def _put(self, url, data):
        full_url = self._base_url + url
        rsp = requests.put(
            full_url, 
            json = data,
            headers = self._headers)
        rsp.raise_for_status()
        return rsp.json()
    
    def _list(self, url, parameters = None):
        full_url = self._base_url + url
        if not parameters is None:
            full_url += '?' + parameters.generate()

        items = []
        has_items = True
        while has_items:
            rsp = requests.get(
                full_url, 
                headers = self._headers)
            rsp.raise_for_status()
            new_items = rsp.json()
            items.extend(new_items)
            rel = [_split_link(link) for link in rsp.headers['Link'].split(',')]
            next = list(filter(lambda item: item[0] == 'next', rel))
            if len(next) == 0:
                has_items = False
            else:
                full_url = next[0][1]

        return items
        
    def get_current_user(self):
        return self._get('/api/v1/users/self')
    
    def get_course(self, course_id):
        return self._get(f'/api/v1/courses/{course_id}')
    
    def get_assignment(self, course_id, assignment_id):
        return self._get(f'/api/v1/courses/{course_id}/assignments/{assignment_id}')

    def list_submissions(self, course_id, assignment_id, parameters = None):
        return self._list(
            f'/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions', 
            parameters = parameters)

    def list_users_in_course(self, course_id, parameters = None):
        return self._list(
            f'/api/v1/courses/{course_id}/users', 
            parameters = parameters)

    def list_students_in_course(self, course_id, parameters = None):
        if parameters is None:
            parameters = Parameters()
        parameters.add('enrollment_type[]', 'student')
        return self._list(
            f'/api/v1/courses/{course_id}/users', 
            parameters = parameters)

    def mark_submission(self, course_id, assignment_id, student_id, score = None, comment = None, rubric = None):
        data = {}
        if not score is None:
            data['submission'] = {
                'posted_grade': score
            }
        if not comment is None:
            data['comment'] = {
                'text_comment': comment
            }
        if not rubric is None:
            data['rubric_assessment'] = rubric

        return self._put(
            f'/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions/{student_id}',
            data
        )