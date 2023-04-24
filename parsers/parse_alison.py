from parsers.components import course_class
from parsers.components import init_browser
from parsers.components import waiter
from parsers.components import db_connector
import time
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


# РАБОТАЕТ ПОЛНОСТЬЮ
# смотреть лайн 135 (заменить кол-во курсов)

URL = "https://alison.com"
SITEMAP = "/sitemap"

COURSES_TOTAL = 0
COURSES_PARSED = 0
BROWSER = init_browser.getBrowser()

LOG = False


def Log(Text):
    if LOG:
        print(Text)


def getCoursesLinks(DBLinks):
    BROWSER.get(URL + SITEMAP)
    html = BROWSER.page_source
    soup = BeautifulSoup(html, "html.parser")
    container = soup.find_all('div', class_="sitemap-col")[1]
    a = container.find_all('a')
    links = []
    for i in range(len(a)):
        # если в базе есть ссылка, то её пропускам и не заносим в список на парсинг
        if not a[i]['href'] in DBLinks:
            links.append(a[i]['href'])
    return links


def getCourseInfoFromLink(Link, WaitTime):
    data = {
        'imageXpath':"//div[@class='l-card__img']//img[last()]",
        'titleXpath':"//h1",
        'descriptionXpath':"//span[@class='l-info__description-full']",
        'tagXpath' : "//ol[@class='breadcrumb ']/li[@class='top-cat']",
        'authorXpath':"//span[@class='course-publisher l-pub__name']",
        'studentsCountXpath':"//span[@class='course-enrolled']",
        "durationXpath":"//div[@class='l-card__includes l-list l-list--tick']//li/span",
        'ratingOneXpath': "//span[@class='course-love'][1]",
        'ratingTwoXpath': "//span[@class='course-like'][1]"
    }
    xpathes = []
    for key in data:
        xpathes.append(data[key])
    err = "Loading page"
    BROWSER.get(Link)

    course = course_class.getCourse()
    try:
        err = "image link"
        waiter.waitAll(BROWSER, WaitTime, [data["imageXpath"]])
        var = BROWSER.find_element(By.XPATH, data['imageXpath']).get_attribute('src')
        Log(f"{err}: {var}")
        course.ImageLink = var

        err = "title"
        waiter.waitAll(BROWSER, WaitTime, [data["titleXpath"]])
        var = BROWSER.find_element(By.XPATH, data['titleXpath']).text
        Log(f"{err}: {var}")
        course.Title = var

        err = "description"
        waiter.waitAll(BROWSER, WaitTime, [data["descriptionXpath"]])
        var = BROWSER.find_element(By.XPATH, data['descriptionXpath']).text
        Log(f"{err}: {var}")
        course.Description = var

        err = "author"
        waiter.waitAll(BROWSER, WaitTime, [data["authorXpath"]])
        var = BROWSER.find_element(By.XPATH, data['authorXpath']).text
        Log(f"{err}: {var}")
        course.Author = var

        err = "tag"
        waiter.waitAll(BROWSER, WaitTime, [data["tagXpath"]])
        var = BROWSER.find_element(By.XPATH, data['tagXpath']).text
        Log(f"{err}: {var}")
        course.Tags.append(var)

        err = "studentsCount"
        waiter.waitAll(BROWSER, WaitTime, [data["studentsCountXpath"]])
        var = BROWSER.find_element(By.XPATH, data['studentsCountXpath']).text
        Log(f"{err}: {var}")
        course.Students = var

        err = "duration"
        waiter.waitAll(BROWSER, WaitTime, [data["durationXpath"]])
        var = BROWSER.find_element(By.XPATH, data["durationXpath"]).text
        Log(f"{err}: {var}")
        course.Duration = var

        # на сайте есть 2 типа рейтинга - очень понравился и просто понравился
        err = "rating one"
        waiter.waitAll(BROWSER, WaitTime, [data["ratingOneXpath"], data["ratingTwoXpath"]])
        var1 = BROWSER.find_element(By.XPATH, data["ratingOneXpath"]).text
        Log(f"{err}: {var1}")
        err = "rating two"
        var2 = BROWSER.find_element(By.XPATH, data["ratingTwoXpath"]).text
        Log(f"{err}: {var2}")
        course.RateCount = int(var1) + int(var2)

        # стандартные поля по-умолчанию
        course.Document = "Sertificate"
        course.Link = Link
        course.Platform = URL
    except:
        Log(f"Error at {err}")
        return False

    return course


def parseBegin(DBLinks):
    global COURSES_TOTAL
    global COURSES_PARSED
    global BROWSER
    links = getCoursesLinks(DBLinks)
    # ссылка на список курсов, нам ни к чему
    links.remove(links[0])
    COURSES_TOTAL = len(links)

    # проходимся по ссылкам
    for link in links[:10]: # удалить [:10]
        err_counter = 5
        course = False
        Log(f">>Course link: {link}")
        while course == False and err_counter != 0:
            Log(f"Course {links.index(link)}, tries left: {err_counter}")
            course = getCourseInfoFromLink(link, 3)
            err_counter = err_counter - 1
        if course != False:
            COURSES_PARSED = COURSES_PARSED + 1
            db_connector.insertCourseToDB(course)
            Log("")
        Log("")


def init(Log):
    global LOG
    LOG = Log
    print(f"Parsing {URL}")
    DBLinks = db_connector.getCoursesLinksByPlatform(URL)
    start = time.time()
    parseBegin(DBLinks)
    print(f"Done. {URL} parsed with {COURSES_PARSED}/{COURSES_TOTAL} courses. Total of {COURSES_PARSED + len(DBLinks)} courses in database. Time: {int(time.time() - start)}sec")
