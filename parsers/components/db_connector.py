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

# возвращает все курсы определенной платформы
def getAllCoursesByPlatform(Platform):
    if not os.path.exists(DB_PATH):
        return []
    
    with open(DB_PATH, 'rb') as f:
        courses = []
        while True:
            try:
                course = pickle.load(f)
                if course.Platform == Platform:
                    courses.append(course)
            except:
                break
    return courses

# вовзращает ссыки курсов определенной платформы
def getCoursesLinksByPlatform(Platform):
    if not os.path.exists(DB_PATH):
        return []
    
    with open(DB_PATH, 'rb') as f:
        coursesLinks = []
        while True:
            try:
                course = pickle.load(f)
                if course.Platform == Platform:
                    coursesLinks.append(course.Link)
            except:
                break
    
    print(f"{Platform} courses in db: {len(coursesLinks)}")

    return coursesLinks

# добавляет список курсов в базу
def insertCoursesListToDB(CoursesList):
    for course in CoursesList:
        insertCourseToDB(course)

# Добавляет 1 курс в базу
def insertCourseToDB(Course):
    with open(DB_PATH, 'ab') as f:
        pickle.dump(Course, f)

# удаляет курсы с базы (не факт что работает)
def removeCourseFromDB(Course):
    courses = getCoursesLinksByPlatform()
    try:
        if Course in courses:
            Course.remove(Course.index(courses))
        with open(DB_PATH, 'wb') as f:
            for course in courses:
                pickle.dump(course, f)
    except:
        print("Error deleting course")