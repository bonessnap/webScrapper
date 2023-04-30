import parsers.components.course_class as course_class
import parsers.components.db_connector as DB
    
# точка входа в парсер
if __name__ == '__main__':

    #from parsers import parse_coursera
    #parse_coursera.init(False)

    from parsers import parse_sololearn
    parse_sololearn.init()

    #from parsers import parse_alison
    #parse_alison.init(False)

    #from parsers import parse_edX
    #parse_edX.init(False)

    #courses = DB.getAllCourses()
    #print("Courses: ", len(courses))
    #courses = list(set(courses))
    #print("Courses: ", len(courses))

    #import parse_skillshare
    #parse_skillshare.init(False)
    print(f"Courses: {len(DB.getAllCourses())}")
    
        