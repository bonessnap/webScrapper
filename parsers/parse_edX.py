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
# СМОТРЕТЬ ЛАЙН 152

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
    counterXpath = "//ul[@class='pagination']/li[last()-1]"
    # куки на сайте
    cookies = "//button[@id='onetrust-accept-btn-handler']"
    WebDriverWait(BROWSER, 10).until(EC.element_to_be_clickable((By.XPATH, cookies)))
    if len(BROWSER.find_elements(By.XPATH, cookies)) != 0:
        BROWSER.find_element(By.XPATH, cookies).click()
    BROWSER.refresh()
    waiter.waitAll(BROWSER, 5, counterXpath)
            
    return int(BROWSER.find_element(By.XPATH, counterXpath).text )


def getCoursesFromPage(DBLinks):
    data = {
        "container" : "//div[@class='base-card-wrapper']",
        "title" : "//div[@class='pgn__card-header-title-md']/span",
        "author" : "//div[@class='pgn__card-header-subtitle-md']",
        "imageLink" : "//img[@class='pgn__card-image-cap']",
        "link" : "//a[@class='base-card-link']"
    }
    coursesList = []
    waiter.waitAll(BROWSER, 5, data.values())
    containers = BROWSER.find_elements(By.XPATH, data["container"])
    titles = BROWSER.find_elements(By.XPATH, data["title"])
    authors = BROWSER.find_elements(By.XPATH, data["author"])
    images = BROWSER.find_elements(By.XPATH, data["imageLink"])
    links = BROWSER.find_elements(By.XPATH, data["link"])

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
    data = {
    "tag" : "(//a[@class='muted-link inline-link'])[2]",
    "description" : "//div[@class='p']",
    "duration" : "(//div[@class='ml-3']/div[@class='h4 mb-0'])[1]",
    "difficulty" : "//span[contains(text(),'Level')]/..",
    "enrolled" : "(//div[@class='small'])[last()]"
    }
    waiter.waitAll(BROWSER, waitTime, data.values())

    course.Description = BROWSER.find_element(By.XPATH, data["description"]).text

    course.Duration = BROWSER.find_element(By.XPATH, data["duration"]).text

    course.Difficulty = BROWSER.find_element(By.XPATH, data["difficulty"]).text.split(": ")[1]

    course.Tags.append(BROWSER.find_element(By.XPATH, data["tag"]).text)

    course.Students = BROWSER.find_element(By.XPATH, data["enrolled"]).text.split("already")[0]
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
    course.Price = BROWSER.find_element(By.XPATH, xpathes[0]).text.split("/n")[1]
    course.Duration = BROWSER.find_element(By.XPATH, xpathes[1]).text
    course.Description = BROWSER.find_element(By.XPATH, xpathes[2]).text
    course.Document = "Certificate"
    return course


def getCourseInfo(Course, waitTime):
    BROWSER.get(Course.Link)
    # на сайте есть 2 типа страниц - страшненькие и красивые
    # мы ждём пока уникальный элемент на странице не появится
    # если элемент 1 появился - страница страшненькая
    # если элемент 2 появился - страница красивая
    xpathes = ["(//div[@class='ml-3']/div[@class='h4 mb-0'])[last()]",
               "//div[@class='main d-flex flex-wrap']"]
    waiter.waitOne(BROWSER, 5, xpathes)
    # если дождались один из 2х тогда работаем дальше, иначе выход
    cheapDesign = bool(len(BROWSER.find_elements(By.XPATH, xpathes[0])))
    log(f"Cheap Design: {cheapDesign}")
    # результат получения данных со странички
    if cheapDesign:
        return parseCheapDesign(Course, waitTime)
    
    return parseNonCheapCourse(Course, waitTime)

def parseBegin(DBLinks):
    global COURSES_PARSED
    global COURSES_TOTAL
    global LOG
    coursesList = []
    pagesCount = 0
    for _ in range(3):
        try:
            pagesCount = getPagesCount()
            break
        except:
            pass    
    
    for i in range(3): # range(pagesCount)
        BROWSER.get(URL + f"/search?tab=course&page={i + 1}")
        for _ in range(3):
            try:
                courses = getCoursesFromPage(DBLinks)
                coursesList.extend(courses)
                break
            except:
                pass

    log(f"Courses: {len(coursesList)}")
    coursesList = list(set(coursesList))
    coursesFromPagesList = []
    log(f"Courses: {len(coursesList)}")
    # проходимся по курсам и собираем инфу с их страницы
    for i in coursesList:
        for _ in range(3):
            try:
                course = getCourseInfo(i, 5)
                coursesFromPagesList.append(copy.copy(course))
                COURSES_PARSED = COURSES_PARSED + 1
                break
            except:
                pass

    db_connector.insertCoursesListToDB(coursesFromPagesList)
    

def init(Log):
    global LOG
    LOG = Log
    print(f"Parsing {URL}")
    DBLinks = db_connector.getCoursesLinksByPlatformName(PLATFORM)
    start = time.time()
    parseBegin(DBLinks)
    print(f"Done. {URL} parsed. Total of {COURSES_PARSED}/{COURSES_TOTAL} courses with {len(DBLinks)} in DataBase. Time: {int(time.time() - start)}sec")
    BROWSER.quit()