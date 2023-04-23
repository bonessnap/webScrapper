import os
import pickle
from parsers.components import course_class
DB_PATH = "Courses.txt"

# возвращает все курсы
def getAllCourses():
    if not os.path.exists(DB_PATH):
        return []
    
    with open(DB_PATH, 'rb') as f:
        courses = []
        while True:
            try:
                courses.append(pickle.load(f))
            except:
                break

    return courses

def getCoursesLinksByURL(PlatformUrl):
    if not os.path.exists(DB_PATH):
        return []
    
    with open(DB_PATH, 'rb') as f:
        coursesLinks = []
        while True:
            try:
                course = pickle.load(f)
                if course.Platform == PlatformUrl:
                    coursesLinks.append(course.Link)
            except:
                break
    
    print(f"{PlatformUrl} courses in db: {len(coursesLinks)}")

    return coursesLinks


def insertCoursesListToDB(CoursesList):
    for course in CoursesList:
        insertCourseToDB(course)

def insertCourseToDB(Course):
    with open(DB_PATH, 'ab') as f:
        pickle.dump(Course, f)

def removeCourseFromDB(Course):
    courses = getCoursesLinksByURL()
    try:
        if Course in courses:
            Course.remove(Course.index(courses))
        with open(DB_PATH, 'wb') as f:
            for course in courses:
                pickle.dump(course, f)
    except:
        print("Error deleting course")