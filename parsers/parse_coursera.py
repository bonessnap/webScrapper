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
COURSES_TOTAL = 0

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


# возвращает с первой странички количество курсов на сайте (такое есть)
def getPagesTotalCount(html):
    pagesCount = int(BROWSER.find_element(By.XPATH, "(//span[@class='cds-119 css-pa6u6k cds-121'])[last()]").text)
    log(f"Pages total: {pagesCount}")
    return pagesCount


# возвращает с первой странички количество страниц с курсами
def getCoursesTotalCount(html):
    log("getCoursesTotalCount()")
    soup = BeautifulSoup(html, "html.parser")

    # эта строка приходит в разных видах, прикол
    coursesTotal = soup.find('h1').find('span').text
    log(f"Courses total (text): {coursesTotal}")
    # Иногда там формат "ЧЧ\xa0ЧЧЧ Результатов"
    if len(coursesTotal.split('\xa0')) == 2:
        log(f"Contains xa0")
        coursesTotal = coursesTotal.split("\xa0")
        log(f"Courses total split('xa0'): {coursesTotal}")
        coursesTotal = coursesTotal[0] + coursesTotal[1].split(' ')[0]
        log(f"Courses total [0] + [1]split(' ')[0]: {coursesTotal}")
    # Иногда там формат "Результатов: ЧЧЧЧЧЧ"
    else:
        log(f"Doesn`t contains xa0")
        coursesTotal = coursesTotal.split(" ")[1]
        log(f"Courses total split(' ')[1]: {coursesTotal}")
    return int(coursesTotal)


# получает курсы со странички и заносит их в список
def getCoursesFromPage(html, CoursesList):
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

        CoursesList.append(course)
        COURSES_PARSED = COURSES_PARSED + 1
        log("")


def parseBegin(CoursesList):
    global PAGES_PARSED
    global COURSES_TOTAL
    global PAGES_TOTAL

    data = {
        "container" : "//li[@class='cds-9 css-0 cds-11 cds-grid-item cds-56 cds-64 cds-76']",
        "pagesCount" : "(//span[@class='cds-119 css-pa6u6k cds-121'])[last()]",
        "nextPageButton" : "//button[@class='label-text box arrow'][last()]"
    }
    BROWSER.get(URL + "/courses")
    waiter.waitAll(BROWSER, 5, [data["container"], data["pagesCount"]])
    html = BROWSER.page_source
    PAGES_TOTAL = getPagesTotalCount(html)
    COURSES_TOTAL = getCoursesTotalCount(html)

    # ПОЛУЧАЕМ КУРСЫ СО /courses
    # 1) получаем код со страницы в html
    # 2) кликаем на "следующая страница" и отправляем браузер в загрузку
    # 3) получаем с html страницы курсы
    pagesCountCurrentQuery = PAGES_TOTAL
    for i in range(pagesCountCurrentQuery)[:5]: #удалить [:5]
        log(f"Parsing page {i + 1}")
        html = BROWSER.page_source
        WebDriverWait(BROWSER, 5).until(EC.element_to_be_clickable((By.XPATH, data["nextPageButton"])))
        BROWSER.find_element(By.XPATH, data["nextPageButton"]).click()
        getCoursesFromPage(html, CoursesList)
        PAGES_PARSED = PAGES_PARSED + 1
        waiter.waitAll(BROWSER, 5, [data["container"]])
        log("\n\n")

    BROWSER.get(URL + "/courses?query=free")
    waiter.waitAll(BROWSER, 5, [data["container"], data["pagesCount"]])
    html = BROWSER.page_source
    pagesCountCurrentQuery = getPagesTotalCount(html)
    PAGES_TOTAL = PAGES_TOTAL + pagesCountCurrentQuery

    for i in range(pagesCountCurrentQuery)[:5]: #удалить [:5]
        log(f"Parsing page {i + 1}")
        WebDriverWait(BROWSER, 5).until(EC.element_to_be_clickable((By.XPATH, data["nextPageButton"])))
        html = BROWSER.page_source
        BROWSER.find_element(By.XPATH, data["nextPageButton"]).click()
        getCoursesFromPage(html, CoursesList)
        PAGES_PARSED = PAGES_PARSED + 1
        waiter.waitAll(BROWSER, 5, [data["container"]])
        log("\n\n")


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
    print(f"Done. {URL} parsed. Total of {COURSES_PARSED}/{COURSES_TOTAL} courses from {PAGES_PARSED}/{PAGES_TOTAL} pages. Time: {int(time.time() - start)}sec")

init([], False)