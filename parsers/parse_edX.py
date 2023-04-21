import parsers.components.course_class as course_class
import time
import parsers.components.init_browser as init_browser
import parsers.components.waiter as waiter
from selenium.webdriver.common.by import By
import copy

# РАБОТАЕТ ПОЛНОСТЬЮ
# СМОТРЕТЬ ЛАЙН 44

URL = "https://www.edx.org"
SITEMAP = "/sitemap"

BROWSER = init_browser.getBrowser()

# сколько всего курсов на сайте
COURSES_TOTAL = 0
# Сколько спарсили
COURSES_PARSED = 0

# тестовый лист с курсами
COURSES_LIST = []
LOG = True

def log(string):
    if LOG:
        print(string)


def getAllTagsLinks():
    BROWSER.get(URL + SITEMAP)
    xpathes = ["(//h2[@class='h3 mb-3'])[3]/..//a"]

    # if Bool
    if waiter.waitAll(BROWSER, 5, xpathes):
        log(f"Sitemap page loaded successfuly")
    else: 
        log("Error at loading sitemap")
        return False

    # формат словаря
    # TagName : Link
    data = {}
    for i in BROWSER.find_elements(By.XPATH, xpathes[0])[:2]: # УБРАТЬ [:2]
        data[f"{i.text}"] = i.get_attribute('href')

    return data

def getCoursesFromTagPage(Link, Tag):
    global COURSES_TOTAL
    CoursesList = []
    BROWSER.get(Link)
    xpathes = [
        "(//div[@class='base-card-wrapper'])",                            # контейнер с курсом
        "//div[@class='pgn__card-header-subtitle-md']/span/span/span"   # блок автора
               ]
    if waiter.waitAll(BROWSER, 5, xpathes):
        log(f"Tag page loaded successfuly")
    else: 
        log("Error at loading tag page")
        return False

    containers = BROWSER.find_elements(By.XPATH, xpathes[0])
    log(f"Containers: {len(containers)}")
    
    # проходимся по контейнерам и собираем с них инфу
    try:
        for container in range(len(containers)):
            container_xpath = xpathes[0] + f"[{container + 1}]"
            log(f"Container: {container + 1}")
            course = course_class.getCourse()

            linkXpath = container_xpath + "/a"
            link = BROWSER.find_element(By.XPATH, linkXpath).get_attribute('href')
            log(f"link: {link}")
            course.Link = link

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
            CoursesList.append(course)
            course.Tags = Tag
            log(" ")
        log(" ")
    except:
        log("Error reading containers")
        return False
    COURSES_TOTAL = COURSES_TOTAL + len(CoursesList)
    return CoursesList

# парсит некрасивую страничку
# Получает обьект курс и время
def parseCheapDesign(Course, waitTime):
    # создаем полную копию чтобы вносить в неё изменения
    # если курс спарсится хорошо, то потом внесём изменения в оригинал
    # а если будет ошибка, то оригинал не пострадает
    course = copy.deepcopy(Course)
    try:
        err = "cheap description"
        # ждём блок описания, блок длительности, блок цены. блок тегов, блок сложности, блок автора
        xpathes = ["//div[@class='p']", 
                       "(//div[@class='ml-3']/div[@class='h4 mb-0'])[1]",
                       "//ul[@class='mb-0 pl-3 ml-1']//span[contains(text(), 'Level')]/.."]
        waiter.waitAll(BROWSER, waitTime, xpathes)

        course.Description = BROWSER.find_element(By.XPATH, xpathes[0]).text
        err = "cheap duration"
        course.Duration = BROWSER.find_element(By.XPATH, xpathes[1]).text

        err = "cheap difficulty"
        course.Difficulty = BROWSER.find_element(By.XPATH, xpathes[2]).text.split(": ")[1]
    except: 
        log(f"Err at {err}")
        return False
    Course = course
    return True

# парсит красивую страничку
# Получает обьект курс и время
def parseNonCheapCourse(Course, waitTime):
    # создаем полную копию чтобы вносить в неё изменения
    # если курс спарсится хорошо, то потом внесём изменения в оригинал
    # а если будет ошибка, то оригинал не пострадает
    course = copy.deepcopy(Course)
    xpathes = ["//div[@class='main d-flex flex-wrap']",
                "(//div[@class='details'])[3]/div[@class='main']",
                "//div[@class='overview-info']"]
    waiter.waitAll(BROWSER, waitTime, xpathes)
    try:
        err = "rich price"
        course.Price = BROWSER.find_element(By.XPATH, xpathes[0]).text.split("/n")[1]
        err = "rich duration"
        course.Duration = BROWSER.find_element(By.XPATH, xpathes[1]).text
        err = "rich description"
        course.Description = BROWSER.find_element(By.XPATH, xpathes[2]).text
        course.Document = "Certificate"
    except:
        log(f"Error at {err}")
        return False
    # если данные спарсились правильно - заносит изменения в оригинал
    # и возвращает True
    Course = course
    return True

def getCourseInfo(Course, waitTime):
    BROWSER.get(Course.Link)
    # на сайте есть 2 типа страниц - страшненькие и красивые
    # мы ждём пока уникальный элемент на странице не появится
    # если элемент 1 появился - страница страшненькая
    # если элемент 2 появился - страница красивая
    xpathes = ["(//div[@class='ml-3']/div[@class='h4 mb-0'])[last()]",
               "//div[@class='main d-flex flex-wrap']"]
    # если дождались один из 2х тогда работаем дальше, иначе выход
    if waiter.waitOne(BROWSER, waitTime, xpathes):
        log(f"Waited one of success!")
    else: return False

    cheapDesign = bool(len(BROWSER.find_elements(By.XPATH, xpathes[0])))
    log(f"Cheap Design: {cheapDesign}")
    # результат получения данных со странички
    res = False
    if cheapDesign:
        res = parseCheapDesign(Course, waitTime)
    else: 
        res = parseNonCheapCourse(Course, waitTime)
    
    return res

def parseBegin(AllCoursesList):
    global COURSES_PARSED
    global COURSES_TOTAL
    global LOG
    courses_local = []
    data = False
    errors_left = 3
    while data == False and errors_left != 0:
        data = getAllTagsLinks()
        errors_left = errors_left - 1

    if data == False:
        return data

    # проходимся по тегам и собираем каждый курс с тега
    for tag in data:
        errors_left = 3
        courses = False
        log(f"{tag} : {data[tag]}")
        while courses == False and errors_left != 0:
            courses = getCoursesFromTagPage(data[tag], tag)
            errors_left = errors_left - 1
        if courses != False:
            courses_local.extend(courses)
        log(" ")

    log(f"Courses count: {len(courses_local)}")

    # проходимся по курсам и собираем инфу с их страницы
    for i in range(len(courses_local)):
        course = False
        errors_left = 3
        while course == False and errors_left != 0:
            course = getCourseInfo(courses_local[i], 5)
            errors_left = errors_left - 1
        if course != False:
            courses_local[i] = course
            COURSES_PARSED = COURSES_PARSED + 1
        else: 
            log(f"Error parsing {i}: {courses_local[i]}")
        log(" ")

    AllCoursesList.extend(courses_local)

def init(AllCourses, Log):
    global LOG
    LOG = Log
    print(f"Parsing {URL}")
    start = time.time()
    parseBegin(AllCourses)
    print(f"Done. {URL} parsed. Total of {COURSES_PARSED}/{COURSES_TOTAL} courses. Time: {int(time.time() - start)}sec")

