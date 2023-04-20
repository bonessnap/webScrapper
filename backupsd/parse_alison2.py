from bs4 import BeautifulSoup
import components.course_class as course_class
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import components.init_browser as init_browser

URL = "https://alison.com"
BROWSER = init_browser.getBrowser()

# сколько всего страниц и курсов на сайте
PAGES_TOTAL = 0
COURSES_TOTAL = 0

# сколько спарсили страниц и курсов
PAGES_PARSED = 0
COURSES_PARSED = 0

# тестовый лист с курсами
COURSES_LIST = []

# необходимость логгирования (debug)
LOG = False

# если при инициализации функции указать log=True, то будет логироваться в консоль инфа
def log(string):
    if LOG:
        print(string)


# возвращает с первой странички количество курсов на сайте (такое есть)
def getPagesTotalCount(html):
    WebDriverWait(BROWSER, 30).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='js-pagination light-theme simple-pagination']//li[last() - 1]")))
    soup = BeautifulSoup(BROWSER.page_source, "html.parser")
    pagesNavigationDiv = soup.find(
        "div", {"class": ["js-pagination", "light-theme", "simple-pagination"]})
    pagesCount = int(pagesNavigationDiv.find_all('li')[-2].text)
    log(f"Pages count: {pagesCount}")
    return pagesCount


# возвращает с первой странички количество страниц с курсами
def getCoursesTotalCount(html):
    WebDriverWait(BROWSER, 30).until(EC.presence_of_all_elements_located((By.XPATH, "//h2")))
    soup = BeautifulSoup(BROWSER.page_source, "html.parser")
    coursesTotal = int(soup.find("span", id="num-results").text)
    log(f"Courses total: {coursesTotal}")
    return coursesTotal


# с html странички считывает все курсы и заносит их в CourseList
def getCoursesFromPage(html, CoursesList):
    global COURSES_PARSED
    soup = BeautifulSoup(html, "html.parser")
    containers = []
    for i in soup.find_all("div", {"class": ["card", "card--white", "card--wide "]}):
        containers.append(i)
    log(f"Courses on page: {len(containers)}")

    for container in range(len(containers)):
        course = course_class.getCourse()
        # данные про курс
        course.Document = containers[container].find('span', {'class': [
                                                     'course-type-1', 'course-type-2', 'course-type-3']}).text.split(' ')[13]
        log(f"Course document: {course.Document}")

        course.ImageLink = containers[container].find('img')['data-src']
        log(f"Course image link: {course.ImageLink}")

        containerInfo = containers[container].find('div', class_='card__info')
        course.Tags.append(containerInfo.find(
            'div', class_='card__top').find('span').text)
        log(f"Course tags: {course.Tags}")

        course.Title = containerInfo.find(
            'div', class_='card__top').find('h3').text
        log(f"Course Title: {course.Title}")

        course.Author = containerInfo.find(
            'span', class_='card__publisher').find('a')['title']
        log(f"Course Author: {course.Author}")

        course.Duration = containers[container].find(
            'span', class_='card__duration').text
        log(f"Course Duration: {course.Duration}")

        course.Students = containers[container].find(
            'span', class_='card__enrolled').text.split(" ")[0]
        course.Students = int(course.Students.split(
            ",")[0] + course.Students.split(",")[0])
        log(f"Course Students: {course.Students}")

        course.Link = containerInfo.find(
            'a', {'class': ['card__more', 'card__more--mobile']})['href']
        log(f"Course Link: {course.Link}")

        course.Price = "Free"
        log(f"Course price: {course.Price}")

        CoursesList.append(course)
        COURSES_PARSED = COURSES_PARSED + 1
        log("")


# начинает парсить
def parseBegin(CoursesList):
    global COURSES_TOTAL
    global PAGES_TOTAL
    global PAGES_PARSED
    BROWSER.get(URL + "/courses?page=1")
    PAGES_TOTAL = getPagesTotalCount(BROWSER.page_source)
    COURSES_TOTAL = getCoursesTotalCount(BROWSER.page_source)

    # 1) Получаем код со страницы в переменную html
    # 2) Отправляем браузер на загрузку
    # 3) Из переменной html считываем курсы в список
    for i in range(PAGES_TOTAL):   # Диапазон [0, X), заменить на range(PAGES_TOTAL) # range(10)
        log(f"Parsing page {i + 1}")
        html = BROWSER.page_source
        BROWSER.get(URL + f"/courses?page={i + 1}")
        getCoursesFromPage(html, CoursesList)
        PAGES_PARSED = PAGES_PARSED + 1
        WebDriverWait(BROWSER, 30).until(EC.presence_of_all_elements_located((By.XPATH, "//ul[@id='mobile-scroll-anchor']/div")))
        log("\n\n")
    
    BROWSER.close()
    BROWSER.quit()

# точка входа в программу
# принимает список в который добавляются курсы и необходимость логгирования (True, False)
def init(AllCourses, log):
    global LOG
    LOG = log
    print(f"Parsing {URL}")
    start = time.time()
    parseBegin(AllCourses)
    print(f"Done. {URL} parsed. Total of {COURSES_PARSED}/{COURSES_TOTAL} courses from {PAGES_PARSED}/{PAGES_TOTAL} pages. Time: {int(time.time() - start)}sec")
