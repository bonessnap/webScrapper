from parsers import parse_alison
from parsers import parse_coursera
from parsers import parse_sololearn
from parsers import parse_edX
import parsers.components.course_class as course_class

Courses = []

def sendCourseToHell(Course):
    global Courses
    Courses.append(Course)
    
# точка входа
if __name__ == '__main__':
    parse_alison.init(Courses, False)
    parse_coursera.init(Courses, False)
    parse_sololearn.init(Courses)
    # этот долго 
    #parse_edX.init(Courses, False)

    print(f"Courses: {len(Courses)}")
