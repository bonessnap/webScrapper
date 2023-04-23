from parsers import parse_alison
from parsers import parse_coursera
from parsers import parse_sololearn
from parsers import parse_edX
import parsers.components.course_class as course_class
import parsers.components.db_connector as DB

Courses = []
    
# точка входа
if __name__ == '__main__':
    parse_coursera.init(False)
    #parse_sololearn.init()
    #parse_alison.init(False)
    # этот долго 
    #parse_edX.init(Courses, False)
    links = DB.getCoursesLinksByURL("https://www.coursera.org")
    samecount = 0
    print(f"Links: {len(links)}")

    for i in range(len(links)):
        for j in range(len(links[i:])):
            if i != j:
                if links[i] == links[j]:
                    samecount = samecount + 1

    print("Same count: ", samecount)
        