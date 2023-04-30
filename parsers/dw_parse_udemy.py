from bs4 import BeautifulSoup
import parsers.components.course_class as course_class
import time
import parsers.components.init_browser as init_browser


## НЕ РАБОТАЕТ, ПРОБЛЕМА С КУКИ И КАПЧОЙ

URL = "https://www.udemy.com"
BROWSER = init_browser.getBrowser()

# сколько всего страниц и курсов на сайте
PAGES_TOTAL = 0
COURSES_TOTAL = 0

# сколько спарсили страниц и курсов
PAGES_PARSED = 0
COURSES_PARSED = 0

# тестовый лист с курсами
COURSES_LIST = []

COOKIE_FILE = "sample.json"

# если при инициализации функции указать log=True, то будет логироваться в консоль инфа
def log(string):
    if LOG:
        print(string)


# возвращает с первой странички количество курсов на сайте (такое есть)
def getPagesTotalCount(html):
    soup = BeautifulSoup(html, "html.parser")
    pagesNavigationDiv = soup.find("div", {"class": ["pagination-module--container--1Dmb0"]})
    pagesCount = pagesNavigationDiv.find('span', class_="ud-heading-sm pagination-module--page--1Ujec").text
    log(f"Pages count: {pagesCount}")
    return pagesCount


# возвращает с первой странички количество курсов на сайте (такое есть)
def getCoursesTotalCount(html):
    soup = BeautifulSoup(html, "html.parser")
    # text = "N Results"
    totalCoursesCount = soup.find('span', class_=['filter-drawer--filter-results--2aNU-'])
    totalCoursesCount = totalCoursesCount.text.split(" ")[0]
    log(f"Courses count: {totalCoursesCount}")
    return int(totalCoursesCount)


def getCoursesFromPage(html, CoursesList):
    global COURSES_PARSED
    soup = BeautifulSoup(html, "html.parser")
    containers = []
    for i in soup.find('div', class_="course-list--container--FuG0T").find_all("div", class_="popper-module--popper--2BpLn"):
        containers.append(i)
    log(f"Courses on page: {len(containers)}")

    for container in range(len(containers)):
        imageLink = containers[container].find('img')['src']
        log(f"Image link: {imageLink}")

        courseLink = URL + containers[container].find('a')['href']
        log(f"Course link: {courseLink}")

        courseTitle = containers[container].find('a').find(text=True, recursive=False)
        log(f"Course Title: {courseTitle}")

        courseDescription = containers[container].find('p', class_= ['ud-text-sm','course-card--course-headline--2DAqq']).text
        log(f"Course Desc: {courseDescription}")

        # "Author 1, Author 2".text.split(", ") = ['Author 1', 'Author 2']
        courseAuthor = containers[container].find('div', class_= 'course-card--instructor-list--nH1OC').text.split(", ")
        log(f"Course Author: {courseAuthor}")
        
        # "4.5 out of 5".text.split(" ")[1].replace('.', ',') = "4,5"
        courseRating = containers[container].find('div', class_="course-card--row--29Y0w").find('span', class_= 'ud-sr-only').text.split(" ")[1].replace('.', ',')
        log(f"Course rating: {courseRating}")

        # "(оценка)".text[1:-1] = "оценка"
        courseRatingCounts = containers[container].find('div', class_="course-card--row--29Y0w").find('span', class_= ['ud-text-xs','course-card--reviews-text--1yloi']).text[1:-1]
        log(f"Course rating counts: {courseRatingCounts}")
        
        courseInfo = containers[container].find('div', class_=['course-card--course-meta-info--2jTzN'])

        # "12.5 total hours".replace('.', ',') = "12,5 total hours"
        courseDuracity = courseInfo.find_all('span')[0].text.replace('.', ',')
        log(f"Course duracity: {courseDuracity}")
        
        courseDifficulty = courseInfo.find_all('span')[2].text
        log(f"Course Difficulty: {courseDifficulty}")

        coursePrice = containers[container].find('div', class_=['price-text--container--103D9','course-card--price-text-container--XIYmk'])
        log(f"Course Price: {coursePrice}")
        log("")


    
def parseBegin(CoursesList):
    global COURSES_TOTAL
    global PAGES_TOTAL
    BROWSER.get(URL + "/courses/development/?has_coding_exercises=true&locale=en_EN&p=1&src=lohp")
    time.sleep(5)

    with open("udemy.html", "w", encoding="utf-8") as file:
        file.write(BROWSER.page_source)

    with open("udemy.html", encoding="utf-8") as file:
        html = file.read()

    PAGES_TOTAL = getPagesTotalCount(html)
    COURSES_TOTAL = getCoursesTotalCount(html)

    for i in range(1, 10):
        html = BROWSER.page_source
        getCoursesFromPage(html, [])
        BROWSER.get(URL + "/courses/development/?has_coding_exercises=true&locale=en_EN&p=" + str(i) + "&src=lohp")
        time.sleep(4)


def init(AllCourses, log):
    global LOG
    LOG = log
    print(f"Parsing {URL}")
    start = time.time()
    parseBegin(AllCourses)
    print(f"Done. {URL} parsed. Total of {COURSES_PARSED}/{COURSES_TOTAL} courses from {PAGES_PARSED}/{PAGES_TOTAL} pages. Time: {int(time.time() - start)}sec")

init([], True)