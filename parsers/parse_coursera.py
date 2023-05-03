from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from parsers.components import course_class
from parsers.components import init_browser
from parsers.components import db_connector
from parsers.components import waiter

# ПОЛНОСТЬЮ РАБОТАЕТ, СМОТРЕТЬ ЛАЙН 153 и 157

URL = "https://www.coursera.org"
PLATFORM = "coursera"
BROWSER = init_browser.getBrowser()
COURSES_PARSED = 0

LOG = False

def log(string):
    if LOG:
        print(string)

# возвращает количество страниц на текущем запросе
def getPagesTotalCount(xpath):
    for _ in range(3):
        try:
            waiter.waitAll(BROWSER, 5, [xpath])
            return int(BROWSER.find_element(By.XPATH, xpath).text)
        except:
            pass
    return 0


# получает курсы со странички и заносит их в список
def getCoursesFromPage(html, Tag, DBLinks):
    soup = BeautifulSoup(html, "html.parser")
    containers = []
    couresList = []
    for i in soup.find_all('div', class_=['css-1pa69gt', 'css-1j8ushu']):
        containers.append(i)
    log(f"Containers: { len(containers)}")

    for i in range(len(containers)):
        course = course_class.getCourse()
        link = URL + containers[i].find('a')['href']
        if link in DBLinks:
            continue
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
        course.Platformlink = URL
        course.PlatformName = PLATFORM
        couresList.append(course)
    return couresList


def parseBegin(DBLinks):
    global LOG
    global BROWSER
    global COURSES_PARSED

    data = {
        # первые 4 блока с тегами и ссылками на поиск курсов по тегу (фильтр ?query=* в адресной строке) внизу страницы
        # эти блоки прилетают в разном виде, иногда 1 иногда 2
        "Queries_type_1" : "(//div[@class='cds-9 rc-SubFooterSection lohp-rebrand css-0 cds-11 cds-grid-item cds-61'])[position() < 5]//a",
        "Queries_type_2" : "(//div[@class='cds-63 rc-SubFooterSection lohp-rebrand css-0 cds-65 cds-grid-item cds-115'])[position() < 5]//a",
        # контейнеры с курсами на странице
        "container" : "//li[@class='cds-9 css-0 cds-11 cds-grid-item cds-56 cds-64 cds-76']",
        # блок в котором указано количество странци по текущему запросу
        "pagesCount" : "//div[@class='pagination-controls-container']/*[last()-1]",
        # кнопка перехода далее, !!!!!!иногда это кнопка, а иногда ссылка <a> внутри <div>!!!!!!!
        "nextPageButton" : "//div[@class='pagination-controls-container']/*[last()]"
    }
    CoursesList = []
    # query - запрос. Адрес выходит coursera.org/courses?query=...
    queries = []
    # tags - название запроса
    tags = []
    BROWSER.get(URL + "/courses")
    # получаем названия тегов и ссылки на фильт по тегам на сайте
    for _ in range(5):
        try:
            waiter.waitOne(BROWSER, 5, [ [data["Queries_type_1"]], data["Queries_type_2"] ] )
            if len(BROWSER.find_elements(By.XPATH, data["Queries_type_1"])) != 0:
                queries = [a.get_attribute('href') for a in BROWSER.find_elements(By.XPATH, data["Queries_type_1"]) if len(a.get_attribute('href').split("/")) == 4]
                tags = [a.text for a in BROWSER.find_elements(By.XPATH, data["Queries_type_2"]) if len(a.get_attribute('href').split("/")) == 4]
            else:
                queries = [a.get_attribute('href') for a in BROWSER.find_elements(By.XPATH, data["Queries_type_2"]) if len(a.get_attribute('href').split("/")) == 4]
                tags = [a.text for a in BROWSER.find_elements(By.XPATH, data["Queries_type_2"]) if len(a.get_attribute('href').split("/")) == 4]
            if len(queries) != 0 and len(tags) != 0:
                break
        except:
            BROWSER.refresh()
            pass
    if len(queries) == 0 or len(tags) == 0:
        return False

    # проходимся по ссылкам
    for query in queries[:2]: # удалить [:2]
        BROWSER.get(query)
        waiter.waitAll(BROWSER, 5, [data["pagesCount"]])
        pages = getPagesTotalCount(data["pagesCount"])
        for page in range(3): # заменить на range(pages)
            for _ in range(3):
                try:
                    waiter.waitAll(BROWSER, 5, [data["container"]])
                    courses = getCoursesFromPage(BROWSER.page_source, tags[queries.index(query)], DBLinks)
                    CoursesList.extend(courses)
                    COURSES_PARSED = COURSES_PARSED + len(courses)
                    break
                except:
                    pass
            # переходим на следующую страницу
            nextPage = False
            for _ in range(3):
                try:
                    # иногда кнопка перехода это блок <div> с ссылкой <a> на следующую страницу
                    waiter.waitAll(BROWSER, 5, [data["nextPageButton"]])
                    navElem = BROWSER.find_element(By.XPATH, data["nextPageButton"])
                    if page != pages - 1:
                        if navElem.tag_name == "a":
                            BROWSER.get(navElem.get_attribute('href'))
                        # иногда кнопка перехода это именно что кнопка <button>
                        else:
                            WebDriverWait(BROWSER, 5).until(EC.element_to_be_clickable((By.XPATH, data["nextPageButton"])))
                            BROWSER.find_element(By.XPATH, data["nextPageButton"]).click()
                        nextPage = True
                        break
                except:
                    pass
            if not nextPage:
                break

    CoursesList = set(CoursesList)
    db_connector.insertCoursesListToDB(CoursesList)

def init(Log):
    global LOG
    LOG = Log
    print(f"Parsing {URL}")
    DBLinks = db_connector.getCoursesLinksByPlatformName(PLATFORM)
    start = time.time()
    parseBegin(DBLinks)
    print(f"Done. {URL} parsed with {COURSES_PARSED}. Total of {COURSES_PARSED + len(DBLinks)} courses in DB. Time: {int(time.time() - start)}sec")
    BROWSER.close()
    BROWSER.quit()