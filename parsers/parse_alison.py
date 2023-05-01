from parsers.components import course_class
from parsers.components import init_browser
from parsers.components import waiter
from parsers.components import db_connector
import time
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


# РАБОТАЕТ ПОЛНОСТЬЮ
# смотреть лайн 109 (заменить кол-во курсов)

URL = "https://alison.com"
PLATFORM = "alison"
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
    return [i['href'] for i in container.find_all('a') if not i['href'] in DBLinks]


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
    BROWSER.get(Link)
    waiter.waitAll(BROWSER, WaitTime, data.values())

    course = course_class.getCourse()
    var = BROWSER.find_element(By.XPATH, data['imageXpath']).get_attribute('src')
    course.ImageLink = var

    var = BROWSER.find_element(By.XPATH, data['titleXpath']).text
    course.Title = var
    var = BROWSER.find_element(By.XPATH, data['descriptionXpath']).text
    course.Description = var

    var = BROWSER.find_element(By.XPATH, data['authorXpath']).text
    course.Author = var

    var = BROWSER.find_element(By.XPATH, data['tagXpath']).text
    course.Tags.append(var)

    var = BROWSER.find_element(By.XPATH, data['studentsCountXpath']).text
    course.Students = var
    var = BROWSER.find_element(By.XPATH, data["durationXpath"]).text
    course.Duration = var

    # на сайте есть 2 типа рейтинга - очень понравился и просто понравился
    var1 = BROWSER.find_element(By.XPATH, data["ratingOneXpath"]).text
    var2 = BROWSER.find_element(By.XPATH, data["ratingTwoXpath"]).text
    course.RateCount = int(var1) + int(var2)

     # стандартные поля по-умолчанию
    course.Document = "Sertificate"
    course.Link = Link
    course.Platformlink = URL
    course.PlatformName = PLATFORM

    return course

def parseBegin(DBLinks):
    global COURSES_TOTAL
    global COURSES_PARSED
    global BROWSER
    links = []
    # получаем все ссылки которых нет в базе данных
    for _ in range(3):
        try:
            links = getCoursesLinks(DBLinks)
            links.remove(links[0])  # [0] - всегда ссылка на список курсов, нам ни к чему
            COURSES_TOTAL = len(links)
            break
        except:
            pass

    for link in links[:10]:
        Log(f">>Course link: {link}")
        for _ in range(3):
            try:
                course = getCourseInfoFromLink(link, 3)
                #db_connector.insertCourseToDB(course)
                COURSES_PARSED = COURSES_PARSED + 1
                break
            except Exception as e:
                print(f"Error parsing {link}")
                pass


def init(Log):
    global LOG
    LOG = Log
    print(f"Parsing {URL}")
    DBLinks = db_connector.getCoursesLinksByPlatformName(PLATFORM)
    DBLinks = []
    start = time.time()
    parseBegin(DBLinks)
    print(f"Done. {URL} parsed with {COURSES_PARSED}/{COURSES_TOTAL} courses. Total of {COURSES_PARSED + len(DBLinks)} courses in database. Time: {int(time.time() - start)}sec")
    BROWSER.close()
    BROWSER.quit()

init(False)