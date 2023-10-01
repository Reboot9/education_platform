import requests

username = 'studentik1'
password = 'abobatest'

base_url = 'http://127.0.0.1:8000/api/'

r = requests.get(f'{base_url}courses/')
r.raise_for_status()

courses = r.json()

available_courses = ', '.join([course['title'] for course in courses])
print(f"Available courses: {available_courses}")

for course in courses:
    course_id = course['id']
    course_title = course['title']

    r = requests.post(f"{base_url}courses/{course_id}/enroll/", auth=(username, password))
    r.raise_for_status()
    print(f'Successfully enrolled in {course_title}')
