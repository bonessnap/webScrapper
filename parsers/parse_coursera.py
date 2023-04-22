from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from components import course_class
from components import browser
from components import waiter

# ПОЛНОСТЬЮ РАБОТАЕТ, СМОТРЕТЬ ЛАЙН 176

URL = "https://www.coursera.org"
BROWSER = browser.getBrowser()

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
    # находим все теги и ссылки на курсы по тегам
    # дегрис это неправильные ссылки, на них нет курсов и они выдают ошибку
    for a in BROWSER.find_elements(By.XPATH, Xpath):
        if len(a.get_attribute('href').split("/")) == 4:
            queries.append(a.get_attribute('href'))
    return queries

def getAllTags(Xpath):
    queries = []
    for a in BROWSER.find_elements(By.XPATH, Xpath):
        if len(a.get_attribute('href').split("/")) == 4:
            queries.append(a.text)
    return queries


# возвращает количество страниц на текущем запросе
def getPagesTotalCount(xpath):
    errors = 3
    pagesCount = False
    while errors != 0 and pagesCount == False:
        errors = errors - 1
        try:
            waiter.waitAll(BROWSER, 5, [xpath])
            pagesCount = int(BROWSER.find_element(By.XPATH, xpath).text)
            log(f"Pages total: {pagesCount}")
        except:
            log(f"err getting pages count")
            pagesCount = False
    return pagesCount

# получает курсы со странички и заносит их в список
def getCoursesFromPage(html, Tag):
    soup = BeautifulSoup(html, "html.parser")
    containers = []
    couresList = []
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

            course.Tags.append(Tag)
            log(f"Tag: {course.Tags}")

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
        log("")
        couresList.append(course)
    return couresList


def parseBegin(AllCoursesList):
    global PAGES_PARSED
    global PAGES_TOTAL
    global LOG
    global BROWSER
    global COURSES_PARSED

    data = {
        # первые 4 блока с тегами и ссылками на поиск курсов по тегу (фильтр ?query=* ) внизу страницы
        "Queries" : "(//div[@class='cds-9 rc-SubFooterSection lohp-rebrand css-0 cds-11 cds-grid-item cds-61'])[position() < 5]//a",
        # контейнеры с курсами на странице
        "container" : "//li[@class='cds-9 css-0 cds-11 cds-grid-item cds-56 cds-64 cds-76']",
        # блок в котором указано количество странци по текущему запросу
        "pagesCount" : "//div[@class='pagination-controls-container']/*[last()-1]",
        # кнопка перехода далее, иногда это кнопка, а иногда ссылка <a> внутри <div>
        "nextPageButton" : "//div[@class='pagination-controls-container']/*[last()]"
    }
    CoursesList = []
    queries = []
    tags = []
    err_counter = 5
    BROWSER.get(URL + "/courses")
    # достаем категории и ссылки на них на стартовой странице
    while len(queries) == 0 and err_counter != 0:
        queries = getAllQueries(data["Queries"])
        tags = getAllTags(data["Queries"])
        err_counter = err_counter - 1
        if len(queries) == 0:
            BROWSER.quit()
            BROWSER = browser.getBrowser()
            BROWSER.get(URL + "/courses")

    log(f"Queries: {len(queries)}")
    if len(queries) == 0 or len(tags) == 0:
        return False

    # проходимся по каждой категории
    for query in queries[:2]: #удалить [:2]
        log(f"Query {queries.index(query)}: {query}")
        BROWSER.get(query)
        waiter.waitAll(BROWSER, 5, [data["pagesCount"]])
        # получаем количество страниц в категории
        pagesCountCurrentQuery = getPagesTotalCount(data["pagesCount"])
        PAGES_TOTAL = pagesCountCurrentQuery + PAGES_TOTAL

        # в каждой категории проходимся по всем страницам
        for i in range(pagesCountCurrentQuery):
            log(f"Parsing page {i + 1}")
            # ждём появления всех контейнеров с курсами и кнопки далее
            courses = False
            course_err_count = 3
            # пробуем считать курсы со страницы трижды
            while courses == False and course_err_count != 0:
                try:
                    waiter.waitAll(BROWSER, 5, [data["container"]])
                    html = BROWSER.page_source
                    courses = getCoursesFromPage(html, tags[queries.index(query)])
                except: 
                    courses = False
                    log("Error reading page")
                course_err_count = course_err_count - 1
            
            # если считали курсы - добавляем в список
            if courses != False:
                log(f"Added {len(courses)} courses")
                CoursesList.extend(courses)
                COURSES_PARSED = COURSES_PARSED + len(courses)
                PAGES_PARSED = PAGES_PARSED + 1
            
            # кнопка навигации иногда это просто button, а иногда - <a> внутри <div> (иллюзия кнопки)
            # понять можно по тексту - в 1м случае текст кнопки без подчеркивания, во втором - с подчерком
            # здесь в цикле пробуем перейти на следующую страницу
            # так же кнопка иногда "мигает" - появляется и пропадает из ДОМ модели
            # waiter сказал что кнопка есть -> она пропала -> не можем нажать
            # без цикла троувит ошибку переодически, в цикле работает как часы
            nav_err_count = 10
            # если в результате нажатий перешли на следующую страницу то останавливаем цикл
            pageNextClicked = False
            while nav_err_count != 0 and not pageNextClicked and i < pagesCountCurrentQuery - 1:
                nav_err_count = nav_err_count - 1
                try:
                    waiter.waitAll(BROWSER, 5, [data["nextPageButton"]])
                    navElem = BROWSER.find_element(By.XPATH, data["nextPageButton"])
                    log(f"Nav is {navElem.tag_name}")
                    if i != pagesCountCurrentQuery - 1:
                        if navElem.tag_name == "a":
                            BROWSER.get(navElem.get_attribute('href'))
                        else:
                            WebDriverWait(BROWSER, 10).until(EC.element_to_be_clickable((By.XPATH, data["nextPageButton"])))
                            BROWSER.find_element(By.XPATH, data["nextPageButton"]).click()
                        pageNextClicked = True
                except:
                    log(f"Nav error")
                    pageNextClicked = False
            log("")
        log("")

    log(f"Courses in list: {len(CoursesList)}")
    set(CoursesList)
    log(f"Courses in clean list: {len(CoursesList)}")

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