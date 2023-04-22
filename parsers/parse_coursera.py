from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from components import course_class
from components import init_browser
from components import waiter

# РАБОТАЕТ, но не идеал, нужно переделать смотреть лайн 158

URL = "https://www.coursera.org"
BROWSER = init_browser.getBrowser()

# сколько всего страниц и курсов на сайте
PAGES_TOTAL = 0

# сколько спарсили страниц и курсов
PAGES_PARSED = 0
COURSES_PARSED = 0

# тестовый лист с курсами
COURSES_LIST = []

LOG = False

# если при инициализации функции указать log=True, то будет логироваться в консоль инфа


def log(string):
    if LOG:
        print(string)


def getAllQueries(Xpath):
    queries = []
    for a in BROWSER.find_elements(By.XPATH, Xpath):
        queries.append(a.get_attribute('href'))
    return queries

# возвращает с первой странички количество курсов на сайте (такое есть)
def getPagesTotalCount(xpath):
    pagesCount = int(BROWSER.find_element(By.XPATH, xpath).text)
    log(f"Pages total: {pagesCount}")
    return pagesCount

# получает курсы со странички и заносит их в список
def getCoursesFromPage(html):
    global COURSES_PARSED
    soup = BeautifulSoup(html, "html.parser")
    containers = []
    for i in soup.find_all('div', class_=['css-1pa69gt', 'css-1j8ushu']):
        containers.append(i)
    log(f"Containers: { len(containers)}")

    for i in range(len(containers)):
        course = course_class.getCourse()
        link = URL + containers[i].find('a')['href']
        course.Link = link
        log(f"Link: {link}")
        imageLink = containers[i].find('img')['src']
        course.ImageLink = imageLink
        log(f"ImageLink: {imageLink}")

        datablocks = containers[i].find('div', class_='css-12svhik')

        # Проверка текста цены поверх картинки
        log(f"Datablocks: {len(datablocks)}")
        if datablocks.find('div', class_="css-14h1y1z") != None:
            datablock = datablocks.find('div', class_="css-14h1y1z")
            price = datablock.find('p').text
            course.Price = price
            log(f"Price: {price}")

        if datablocks.find('div', class_="css-ilhc4l") != None:
            datablock = datablocks.find('div', class_="css-ilhc4l")
            # проверка верхней части блока под картинкой
            upperBlock = datablock.find('div', class_='css-1rj417c')
            author = upperBlock.find(
                'span', class_=['cds-33', 'css-2fzscr', 'cds-35']).text
            course.Author = author
            log(f"Author: {author}")
            title = upperBlock.find('h2').text
            course.Title = title
            log(f"Title: {title}")
            tags = upperBlock.find(
                'p', class_=['cds-33', 'css-5or6ht', 'cds-35'])
            if tags != None:
                tags = tags.text.split(": ")[1].split(", ")
                course.Tags = tags
                log(f"Tags: {tags}")

            # проверка нижней части блока под картинкой
            ratingBlock = datablock.find('div', class_='css-pn23ng')
            if ratingBlock != None:
                ratingText = ratingBlock.text.split("(")
                rating = ratingText[0]
                course.Rate = rating
                log(f"Rating: {rating}")
                ratesCount = ratingText[1].split(" ")[1][:-1]
                course.RateCount = ratesCount
                log(f"Rates amount: {ratesCount}")

            lastInfoBlock = datablock.find_all(
                'p', class_=['cds-33', 'css-14d8ngk', 'cds-35'])[-1]
            if lastInfoBlock != None:
                log(f"Last info block: { lastInfoBlock}")
                lastInfoBlock = lastInfoBlock.text.split("·")
                log(f"Last info block split: {lastInfoBlock}")
                if lastInfoBlock[0] != "Можно использовать как зачетные единицы":
                    difficulty = lastInfoBlock[0]
                    course.Difficulty = difficulty
                    log(f'Difficulty: {difficulty}')
                    duration = lastInfoBlock[2]
                    course.Duration = duration
                    log(f'Duration: {duration}')

        COURSES_PARSED = COURSES_PARSED + 1
        log("")
        return course


def parseBegin(AllCoursesList):
    global PAGES_PARSED
    global COURSES_TOTAL
    global PAGES_TOTAL
    global LOG

    data = {
        # первые 4 блока с ссылками 
        "Queries" : "(//div[@class='cds-9 rc-SubFooterSection lohp-rebrand css-0 cds-11 cds-grid-item cds-61'])[position() < 5]//a",
        # контейнеры с курсами на странице
        "container" : "//li[@class='cds-9 css-0 cds-11 cds-grid-item cds-56 cds-64 cds-76']",
        # блок в котором указано количество странци по текущему запросу
        "pagesCount" : "//div[@class='pagination-controls-container']/*[last()-1]",
        # кнопка перелистывания
        "nextPageButton" : "//div[@class='pagination-controls-container']/*[last()]"
    }
    CoursesList = []
    queries = []
    err_counter = 5
    BROWSER.get(URL + "/courses")
    while len(queries) == 0 and err_counter != 0:
        waiter.waitAll(BROWSER, 5, [data["Queries"]])
        queries = getAllQueries(data["Queries"])
        err_counter = err_counter - 1
        if len(queries) == 0:
            BROWSER.refresh()

    log(f"Queries: {len(queries)}")
    if len(queries) == 0:
        return False
    
    html = BROWSER.page_source

    for query in queries[:5]: #удалить [:2]
        log(f"Query {queries.index(query)}: {query}")
        BROWSER.get(query)
        waiter.waitAll(BROWSER, 5, [data["container"], data["pagesCount"]])
        pagesCountCurrentQuery = getPagesTotalCount(data["pagesCount"])
        PAGES_TOTAL = pagesCountCurrentQuery + PAGES_TOTAL
        for i in range(pagesCountCurrentQuery)[:5]: #удалить [:5]
            log(f"Parsing page {i + 1}")
            waiter.waitAll(BROWSER, 5, [data["container"]])
            html = BROWSER.page_source
            LOG = False
            course = getCoursesFromPage(html)
            LOG = True
            if not any(x.Link == course.Link for x in CoursesList):
                CoursesList.append(course)
            
            waiter.waitAll(BROWSER, 5, [data["nextPageButton"]])
            BROWSER.find_element(By.XPATH, data["nextPageButton"]).click()
            PAGES_PARSED = PAGES_PARSED + 1
            log("")
        log("")

    log(f"Courses in list: {len(CoursesList)}")

    BROWSER.close()
    BROWSER.quit()

# точка входа в программу
# принимает список в который добавляются курсы и необходимость логгирования (True, False)


def init(AllCourses, Log):
    global LOG
    LOG = Log
    print(f"Parsing {URL}")
    start = time.time()
    parseBegin(AllCourses)
    print(f"Done. {URL} parsed. Total of {COURSES_PARSED} courses from {PAGES_PARSED}/{PAGES_TOTAL} pages. Time: {int(time.time() - start)}sec")

init([], True)