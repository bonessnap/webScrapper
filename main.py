import parsers.components.course_class as course_class
import parsers.components.db_connector as DB
import time
    
# точка входа
if __name__ == '__main__':
    #from parsers import parse_coursera
    #parse_coursera.init(False)
    from parsers import parse_sololearn
    parse_sololearn.init()
    #from parsers import parse_alison
    #parse_alison.init(False)
    #from parsers import parse_edX
    #parse_edX.init(False)
    courses = DB.getAllCourses()
    for i in courses:
        print()
        i.printSelf()
        time.sleep(5)
        