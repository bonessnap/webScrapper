from parsers import parse_alison
from parsers import parse_coursera
from parsers import parse_sololearn
from parsers import parse_edX
import parsers.components.course_class as course_class
import parsers.components.db_connector as DB
    
# точка входа
if __name__ == '__main__':
    parse_coursera.init(False)
    parse_sololearn.init()
    parse_alison.init(False)
    parse_edX.init(False)
    courses = []
    courses.extend(DB.getAllCoursesByPlatform("https://www.edx.org"))
    courses.extend(DB.getAllCoursesByPlatform("https://alison.com"))
    courses.extend(DB.getAllCoursesByPlatform("https://www.coursera.org"))
    courses.extend(DB.getAllCoursesByPlatform("https://www.sololearn.com"))
    print(f"Coruses: {len(courses)}")
        