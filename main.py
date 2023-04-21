from parsers import parse_alison
from parsers import parse_coursera
from parsers import parse_sololearn
import dw_parse_edX
import parsers.components.course_class as course_class
import time

Courses = []

def sendCourseToHell(Course):
    global Courses
    Courses.append(Course)
    
if __name__ == '__main__':
    parse_alison.init(Courses, False)
    parse_coursera.init(Courses, False)
    parse_sololearn.init(Courses)
    dw_parse_edX.init(Courses, False)
    time.sleep(5)

    print(f"Res: {len(Courses)}")
