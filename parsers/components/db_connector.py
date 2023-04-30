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
def getCoursesLinksByPlatformName(Platform):
    if not os.path.exists(DB_PATH):
        return []
    
    with open(DB_PATH, 'rb') as f:
        coursesLinks = []
        while True:
            try:
                course = pickle.load(f)
                if course.PlatformName == Platform:
                    coursesLinks.append(course.Link)
            except:
                break
    
    print(f"{Platform} courses in db: {len(coursesLinks)}")

    return coursesLinks

# добавляет список курсов в базу
def insertCoursesListToDB(CoursesList):
    [insertCourseToDB(course) for course in CoursesList]

# Добавляет 1 курс в базу
def insertCourseToDB(Course):
    with open(DB_PATH, 'ab') as f:
        pickle.dump(Course, f)