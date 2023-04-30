from parsers.components import course_class
from parsers.components import init_browser
from parsers.components import db_connector
from parsers.components import waiter
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import copy

# РАБОТАЕТ ПОЛНОСТЬЮ
# СМОТРЕТЬ ЛАЙН 191

URL = "https://www.edx.org"
PLATFORM = "edx"
SITEMAP = "/sitemap"

BROWSER = init_browser.getBrowser()

# сколько всего курсов на сайте
COURSES_TOTAL = 0
# Сколько спарсили
COURSES_PARSED = 0

LOG = False

def log(string):
    if LOG:
        log(string)


def getPagesCount():
    BROWSER.get(URL + "/search?tab=course")  
    errors = 5
    counterXpath = "//ul[@class='pagination']/li[last()-1]"
    cookies = "//button[@id='onetrust-accept-btn-handler']"
    WebDriverWait(BROWSER, 10).until(EC.element_to_be_clickable((By.XPATH, cookies)))
    if len(BROWSER.find_elements(By.XPATH, cookies)) != 0:
        BROWSER.find_element(By.XPATH, cookies).click()
    BROWSER.refresh()
    pagesCount = False
    while errors != 0 and pagesCount == False:
        errors = errors - 1
        try:
            waiter.waitAll(BROWSER, 5, counterXpath)
            pagesCount = BROWSER.find_element(By.XPATH, counterXpath).text  
        except:
            pagesCount = False
            
    return int(pagesCount)


def getCoursesFromPage(DBLinks):
    data = {
        "container" : "//div[@class='base-card-wrapper']",
        "title" : "//div[@class='pgn__card-header-title-md']/span",
        "author" : "//div[@class='pgn__card-header-subtitle-md']",
        "imageLink" : "//img[@class='pgn__card-image-cap']",
        "link" : "//a[@class='base-card-link']"
    }
    coursesList = []
    xpathes = []
    for key in data:
        xpathes.append(data[key])
    waiter.waitAll(BROWSER, 5, xpathes)
    errs = 5
    success = False
    while errs != 0 and not success:
        errs = errs - 1
        try:
            containers = BROWSER.find_elements(By.XPATH, data["container"])
            titles = BROWSER.find_elements(By.XPATH, data["title"])
            authors = BROWSER.find_elements(By.XPATH, data["author"])
            images = BROWSER.find_elements(By.XPATH, data["imageLink"])
            links = BROWSER.find_elements(By.XPATH, data["link"])
            success = True
        except:
            success = False

    if len(containers) == 0:
        return False


    for i in range(len(containers)):
        if links[i] in DBLinks:
            continue
        course = course_class.getCourse()
        course.Author = authors[i].text
        course.Title = "".join(titles[i].text.split("\n"))
        course.ImageLink = images[i].get_attribute('src')
        course.Link = links[i].get_attribute('href')
        course.Platformlink = URL
        course.PlatformName = PLATFORM
        coursesList.append(course)
    
    return coursesList


# парсит некрасивую страничку
# Получает обьект курс и время
def parseCheapDesign(Course, waitTime):
    # создаем полную копию чтобы вносить в неё изменения
    # если курс спарсится хорошо, то потом внесём изменения в оригинал
    # а если будет ошибка, то оригинал не пострадает
    course = copy.deepcopy(Course)
    try:
        data = {
        "tag" : "(//a[@class='muted-link inline-link'])[2]",
        "description" : "//div[@class='p']",
        "duration" : "(//div[@class='ml-3']/div[@class='h4 mb-0'])[1]",
        "difficulty" : "//span[contains(text(),'Level')]/..",
        "enrolled" : "(//div[@class='small'])[last()]"
        }
        xpathes = [data[key] for key in data]
        waiter.waitAll(BROWSER, waitTime, xpathes)

        err = "cheap description"
        course.Description = BROWSER.find_element(By.XPATH, data["description"]).text

        err = "cheap duration"
        course.Duration = BROWSER.find_element(By.XPATH, data["duration"]).text

        err = "cheap difficulty"
        course.Difficulty = BROWSER.find_element(By.XPATH, data["difficulty"]).text.split(": ")[1]

        err = "cheap tag"
        course.Tags.append(BROWSER.find_element(By.XPATH, data["tag"]).text)

        err = "cheap enrolled"
        course.Students = BROWSER.find_element(By.XPATH, data["enrolled"]).text.split("already")[0]
    except: 
        log(f"Err at {err} in {course.Link}")
        return False
    return course

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
        log(f"Error at {err} in {course.Link}")
        return False
    # если данные спарсились правильно - заносит изменения в оригинал
    # и возвращает True
    return course


def getCourseInfo(Course, waitTime):
    BROWSER.get(Course.Link)
    # на сайте есть 2 типа страниц - страшненькие и красивые
    # мы ждём пока уникальный элемент на странице не появится
    # если элемент 1 появился - страница страшненькая
    # если элемент 2 появился - страница красивая
    xpathes = ["(//div[@class='ml-3']/div[@class='h4 mb-0'])[last()]",
               "//div[@class='main d-flex flex-wrap']"]
    # если дождались один из 2х тогда работаем дальше, иначе выход
    if not waiter.waitOne(BROWSER, waitTime, xpathes):
        return False

    cheapDesign = bool(len(BROWSER.find_elements(By.XPATH, xpathes[0])))
    log(f"Cheap Design: {cheapDesign}")
    # результат получения данных со странички
    if cheapDesign:
        result = parseCheapDesign(Course, waitTime)
    else: 
        result = parseNonCheapCourse(Course, waitTime)
    
    return result

def parseBegin(DBLinks):
    global COURSES_PARSED
    global COURSES_TOTAL
    global LOG
    coursesList = []
    pagesCount = getPagesCount()    
    log(pagesCount)
    
    for i in range(4): # range(pagesCount)
        errors_left = 5
        courses = False
        BROWSER.get(URL + f"/search?tab=course&page={i + 1}")
        while errors_left != 0 and courses == False:
            errors_left = errors_left - 1
            try:
                courses = getCoursesFromPage(DBLinks)
            except:
                courses = False
        if courses != False:
            coursesList.extend(courses)

    log(f"Courses: {len(coursesList)}")
    coursesList = list(set(coursesList))
    coursesFromPagesList = []
    log(f"Courses: {len(coursesList)}")
    # проходимся по курсам и собираем инфу с их страницы
    for i in range(len(coursesList)):
        log(f"I: {coursesList.index(coursesList[i])}")
        parsingResult = False
        errors_left = 3
        while parsingResult == False and errors_left != 0:
            parsingResult = getCourseInfo(coursesList[i], 5)
            errors_left = errors_left - 1
        if parsingResult != False:
            coursesFromPagesList.append(copy.copy(parsingResult))
            COURSES_PARSED = COURSES_PARSED + 1
        else: 
            log(f"Error parsing {i}: {coursesList[i]}")
        log(" ")

    db_connector.insertCoursesListToDB(coursesFromPagesList)
    

def init(Log):
    global LOG
    LOG = Log
    print(f"Parsing {URL}")
    DBLinks = db_connector.getCoursesLinksByPlatform(URL)
    start = time.time()
    parseBegin(DBLinks)
    print(f"Done. {URL} parsed. Total of {COURSES_PARSED}/{COURSES_TOTAL} courses with {len(DBLinks)} in DataBase. Time: {int(time.time() - start)}sec")

