from bs4 import BeautifulSoup
import components.course_class as course_class
import time
import components.init_browser as init_browser
import os

# РАБОТАЕТ ЫЫЫЫЫЫЫЫЫЫЫЫЫ #
# СМОТРЕТЬ 98 ЛАЙН
# В ДАННЫЙ МОМЕНТ РАБОТАЕТ НО ПАРСИТ ТОЛЬКО 1Ю СТРАНИЧКУ (МОЖНО ИЗМЕНИТЬ)

# ссылка на доменное имя
URL = "https://alison.com"
# обьект браузер
BROWSER = init_browser.getBrowser()
# Количество курсов на сайте
COURSES_COUNT = 0
# Количество страниц которые спарсили
PAGES_COUNT = 0
COURSES = []

def getPageToFile(link, sleepTime):
    BROWSER.get(link)
    time.sleep(sleepTime)
    # записываем результат в файлик
    with open("page_alison.html", "w", encoding="utf-8") as file:
        file.write(BROWSER.page_source)


# здесь парсится каждая страничка с курсами
# page1, page2.... page186
def parsePageWithCourses(numPage):
    getPageToFile(URL + f"/courses?page={numPage + 1}", 2)

    global COURSES
    global COURSES_PARSE
    html = ""
    with open("page_alison.html", encoding="utf-8") as file:
        html = file.read()
    soup = BeautifulSoup(html, "html.parser")

    containers = []
    for i in soup.find_all("div", {"class": ["card", "card--white", "card--wide "]}):
        containers.append(i)
    images = []
    for i in soup.find_all('img', class_="lazyload"):
        images.append(i['data-src'])

    for container in range(len(containers)):
        global COURSES
        course = course_class.getCourse()
        # данные про курс
        course.Document = containers[container].find('span', {'class': [
                                                     'course-type-1', 'course-type-2', 'course-type-3']}).text.split(' ')[13]
        course.ImageLink = containers[container].find('img')['data-src']
        containerInfo = containers[container].find('div', class_='card__info')
        course.Tags.append(containerInfo.find(
            'div', class_='card__top').find('span').text)
        course.Title = containerInfo.find(
            'div', class_='card__top').find('h3').text
        course.Author = containerInfo.find(
            'span', class_='card__publisher').find('a')['title']
        course.Duration = containers[container].find(
            'span', class_='card__duration').text
        course.Students = containers[container].find(
            'span', class_='card__enrolled').text.split(" ")[0]
        course.Students = int(course.Students.split(
            ",")[0] + course.Students.split(",")[0])
        course.Link = containerInfo.find(
            'a', {'class': ['card__more', 'card__more--mobile']})['href']
        course.Price = "Free"

        # для каждого курса переходим на его страничку и узнаем описание оттуда
        BROWSER.get(course.Link)
        time.sleep(2)
        containerInfo = BeautifulSoup(BROWSER.page_source, 'html.parser')
        course.Description = containerInfo.find(
            'span', class_="l-info__description-full").text

        COURSES.append(course)


def parseBegin():
    global COURSES_COUNT
    global PAGES_COUNT
    getPageToFile(URL + "/courses?page=1", 5)
    html = ""
    with open("page_alison.html", encoding="utf-8") as file:
        html = file.read()

    soup = BeautifulSoup(html, "html.parser")
    COURSES_COUNT = soup.find('span', {'id': 'num-results'}).text

    pages = soup.find(
        "div", {"class": ["js-pagination", "light-theme", "simple-pagination"]})
    pages = int(pages.find_all('li')[-2].text)

    for i in range(1): # ПОМЕНЯТЬ НА range(pages) чтобы спарсить всё
        parsePageWithCourses(i)
        PAGES_COUNT = PAGES_COUNT + 1

    BROWSER.close()
    BROWSER.quit()
    os.remove("page_alison.html")


def init(AllCourses):
    print(f"Parsing {URL}")
    start = time.time()
    parseBegin()
    print(f"Done. {URL} parsed. Total of {len(COURSES)} courses form {PAGES_COUNT} pages. Time: {int(time.time() - start)}sec")
    AllCourses.extend(COURSES)

