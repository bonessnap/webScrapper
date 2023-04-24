from parsers.components import course_class
from parsers.components import init_browser
from parsers.components import db_connector
from parsers.components import waiter
from selenium.webdriver.common.by import By
import time
import copy

URL = "https://www.edx.org"
SITEMAP = "/sitemap"

BROWSER = init_browser.getBrowser()

COURSES_TOTAL = 0
COURSES_PARSED = 0

LOG = True

def log(string):
    if LOG:
        print(string)

def getAllTagsLinks():
    BROWSER.get(URL + SITEMAP)
    xpathes = ["(//h2[@class='h3 mb-3'])[3]/..//a"]

    # if Bool
    errors_left = 3
    while errors_left != 0:
        if not waiter.waitAll(BROWSER, 5, xpathes):
            errors_left = errors_left - 1
        else: break

    if len(BROWSER.find_elements(By.XPATH, xpathes[0])) == 0:
        return False

    # формат словаря
    # TagName : Link
    data = {}
    for i in BROWSER.find_elements(By.XPATH, xpathes[0])[:2]: # УБРАТЬ [:2]
        data[f"{i.text}"] = i.get_attribute('href')

    return data


def getCoursesFromTagPageContainers(Link, Tag, DBLinks, xpathes):
    containers = BROWSER.find_elements(By.XPATH, xpathes[0])
    coursesList = []
    try:
        for container in range(len(containers)):
            container_xpath = xpathes[0] + f"[{container + 1}]"
            log(f"Container: {container + 1}")
            course = course_class.getCourse()

            linkXpath = container_xpath + "/a"
            link = BROWSER.find_element(By.XPATH, linkXpath).get_attribute('href')
            log(f"link: {link}")
            course.Link = link
            if Link in DBLinks:
                continue

            titleXpath = container_xpath + "//div[@class='pgn__card-header-title-md']" + "/span"
            title = BROWSER.find_element(By.XPATH, titleXpath).text.split("\n")
            title = " ".join(title)
            log(f"Title: {title}")
            course.Title = title

            imageLink = container_xpath + "//img"
            imageLink = BROWSER.find_element(By.XPATH, imageLink).get_attribute('src')
            log(f"Image link: {imageLink}")
            course.ImageLink = imageLink

            authorXpath = container_xpath + "//div[@class='pgn__card-header-subtitle-md']"
            author = BROWSER.find_element(By.XPATH, authorXpath).text
            log(f"Author: {author}")
            course.Author = author

            documentXpath = container_xpath + "//span[@class='badge badge-primary']"
            document = BROWSER.find_element(By.XPATH, documentXpath).text
            log(f"Document: {document}")
            if document != "Course":
                course.Document = document
            course.Tags.append(Tag)
            course.Platform = URL
            log(f"Course tag: {course.Tags}")
            coursesList.append(course)
            log(" ")
        log(" ")
    except:
        log("Error reading containers")
        return False
    return coursesList

def getCoursesFromTagPage(Link, TagName, DBLinks):
    BROWSER.get(Link)
    data = {"CourseContainer" : "(//div[@class='base-card-wrapper'])",
            "AuthorBlock" : "//div[@class='pgn__card-header-subtitle-md']/span/span/span"}
    xpathes = []
    for tag in data:
        xpathes.append(data[tag])

    errors_left = 5
    Courses = False
    while Courses == False and errors_left != 0:
        errors_left = errors_left - 1
        try:
            waiter.waitAll(BROWSER, 5, xpathes)
            courses = getCoursesFromTagPageContainers(Link, )
        except:
            Courses = False

def parseBegin(DBLinks):
    global COURSES_PARSED
    global COURSES_TOTAL
    global LOG
    # tag : link
    data = getAllTagsLinks()
    if data == False:
        return data

    coursesList = []

    # проходимся по тегам и собираем каждый курс с тега
    for tag in data:
        errors_left = 3
        courses = False
        log(f"{tag} : {data[tag]}")
        while courses == False and errors_left != 0:
            courses = getCoursesFromTagPage(data[tag], tag, DBLinks)
            errors_left = errors_left - 1
        if courses != False:
            coursesList.extend(courses)
        log(" ")

    print(f"Courses count: {len(coursesList)}")

    coursesList = list(set(coursesList))
    print(f"Courses set count: {len(coursesList)}")
    # проходимся по курсам и собираем инфу с их страницы
    for i in range(len(coursesList[:20])):
        course = False
        errors_left = 3
        while course == False and errors_left != 0:
            course = getCourseInfo(coursesList[i], 5)
            errors_left = errors_left - 1
        if course != False:
            coursesList[i] = course
            COURSES_PARSED = COURSES_PARSED + 1
        else: 
            log(f"Error parsing {i}: {coursesList[i]}")
        log(" ")

    db_connector.insertCoursesListToDB(coursesList)