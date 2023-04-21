from parsers.components import course_class
from parsers.components import init_browser
from parsers.components import waiter
import time
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


# РАБОТАЕТ ПОЛНОСТЬЮ
# смотреть лайн 126 (заменить кол-во курсов)

URL = "https://alison.com"
SITEMAP = "/sitemap"

COURSES_TOTAL = 0
COURSES_PARSED = 0
BROWSER = init_browser.getBrowser()

LOG = False


def Log(Text):
    if LOG:
        print(Text)


def getCoursesLinks():
    BROWSER.get(URL + SITEMAP)
    html = BROWSER.page_source
    soup = BeautifulSoup(html, "html.parser")
    container = soup.find_all('div', class_="sitemap-col")[1]
    links = container.find_all('a')
    for i in range(len(links)):
        links[i] = links[i]['href']
    return links


def getCourseInfoFromLink(Link, WaitTime):
    imageXpath = "//div[@class='l-card__img']//img[last()]"
    titleXpath = "//h1"
    descriptionXpath = "//span[@class='l-info__description-full']"
    tagXpath = "//ol[@class='breadcrumb ']/li[@class='top-cat']"
    authorXpath = "//span[@class='course-publisher l-pub__name']"
    studentsCountXpath = "//span[@class='course-enrolled']"
    durationXpath = "//div[@class='l-card__includes l-list l-list--tick']//li/span"
    ratingOneXpath = "//span[@class='course-love'][1]"
    ratingTwoXpath = "//span[@class='course-like'][1]"
    xpathes = [imageXpath, titleXpath, descriptionXpath, tagXpath, authorXpath,
               studentsCountXpath, durationXpath, ratingOneXpath, ratingTwoXpath]


    err = "Loading page"
    try:
        BROWSER.get(Link)
        waiter.waitAll(BROWSER, WaitTime, xpathes)
    except:
        print(f"Error at {err}")
        return False

    course = course_class.getCourse()
    try:
        err = "image link"
        var = BROWSER.find_element(By.XPATH, imageXpath).get_attribute('src')
        Log(f"{err}: {var}")
        course.ImageLink = var

        err = "title"
        var = BROWSER.find_element(By.XPATH, titleXpath).text
        Log(f"{err}: {var}")
        course.Title = var

        err = "description"
        var = BROWSER.find_element(By.XPATH, descriptionXpath).text
        Log(f"{err}: {var}")
        course.Description = var

        err = "author"
        var = BROWSER.find_element(By.XPATH, authorXpath).text
        Log(f"{err}: {var}")
        course.Author = var

        err = "tag"
        var = BROWSER.find_element(By.XPATH, tagXpath).text
        Log(f"{err}: {var}")
        course.Tags = var

        err = "studentsCount"
        var = BROWSER.find_element(By.XPATH, studentsCountXpath).text
        Log(f"{err}: {var}")
        course.Students = var

        err = "duration"
        var = BROWSER.find_element(By.XPATH, durationXpath).text
        Log(f"{err}: {var}")
        course.Duration = var

        # на сайте есть 2 типа рейтинга - очень понравился и просто понравился
        err = "rating one"
        var1 = BROWSER.find_element(By.XPATH, ratingOneXpath).text
        Log(f"{err}: {var1}")
        err = "rating two"
        var2 = BROWSER.find_element(By.XPATH, ratingTwoXpath).text
        Log(f"{err}: {var2}")
        course.RateCount = int(var1) + int(var2)

        # стандартные поля по-умолчанию
        course.Document = "Sertificate"
        course.Link = Link
    except:
        Log(f"Error at {err}")
        return False

    return course


def parseBegin(CoursesList):
    global COURSES_TOTAL
    global COURSES_PARSED
    global BROWSER
    links = getCoursesLinks()
    links.remove(links[0])
    COURSES_TOTAL = len(links)

    # УБРАТЬ [:10]
    for link in links[:10]: # удалить [:10]
        err_counter = 5
        course = False
        Log(f">>Course link: {link}")
        while course == False and err_counter != 0:
            Log(f"Course {links.index(link)}, tries left: {err_counter}")
            course = getCourseInfoFromLink(link, 5)
            err_counter = err_counter - 1
        if course != False:
            COURSES_PARSED = COURSES_PARSED + 1
            CoursesList.append(course)
            Log("")
        Log("")


def init(AllCourses, Log):
    global LOG
    LOG = Log
    print(f"Parsing {URL}")
    start = time.time()
    parseBegin(AllCourses)
    print(f"Done. {URL} parsed. Total of {COURSES_PARSED}/{COURSES_TOTAL} courses. Time: {int(time.time() - start)}sec")
