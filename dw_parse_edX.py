import components.course_class as course_class
import time
import components.init_browser as init_browser
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import copy

URL = "https://www.edx.org"

COURSES_URL = "/search?tab=course"

BROWSER = init_browser.getBrowser()

# сколько всего страниц и курсов на сайте
PAGES_TOTAL = 0
COURSES_TOTAL = 0

# сколько спарсили страниц и курсов
PAGES_PARSED = 0
COURSES_PARSED = 0

# тестовый лист с курсами
COURSES_LIST = []

LOG = True


def log(string):
    if LOG:
        print(string)


def getCoursesTotalCount():
    WebDriverWait(BROWSER, 10).until(EC.presence_of_all_elements_located(
        (By.XPATH, "//div[@class='small result-count']")))
    coursesTotal = BROWSER.find_element(
        By.XPATH, "//div[@class='small result-count']").text.split(" ")[0]
    return int(coursesTotal)


def getPagesTotalCount():
    WebDriverWait(BROWSER, 10).until(EC.presence_of_all_elements_located(
        (By.XPATH, "//div[@class='mt-4.5']//ul[@class='pagination']/li[last() -1]")))
    pagesTotal = BROWSER.find_element(
        By.XPATH, "//div[@class='mt-4.5']//ul[@class='pagination']/li[last() -1]").text
    return int(pagesTotal)


def getCoursesFromPage(CoursesList):
    WebDriverWait(BROWSER, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='base-card-wrapper']")))
    WebDriverWait(BROWSER, 10).until(EC.presence_of_all_elements_located((By.XPATH,  "//div[@class='pgn__card-header-subtitle-md']/span/span/span")))
    containers = BROWSER.find_elements(By.XPATH, "//div[@class='base-card-wrapper']")
    log(f"Containers: {len(containers)}")
    for container in range(len(containers)):  # заменить на range(len(containers))
        container_xpath = "(//div[@class='card-container d-flex flex-wrap']/div[@class='base-card-wrapper'])" + f"[{container + 1}]"
        log(f"Container: {container + 1}")
        log(f"Container xpath: {container_xpath}")
        course = course_class.getCourse()

        linkXpath = container_xpath + "/a"
        link = BROWSER.find_element(By.XPATH, linkXpath).get_attribute('href')
        log(f"link: {link}")
        course.Link = link

        titleXpath = container_xpath + "//div[@class='pgn__card-header-title-md']" + "/span"
        title = BROWSER.find_element(By.XPATH, titleXpath).text.split("\n")
        title = " ".join(title)
        log(f"Title: {title}")
        course.Title = title

        imageLink = container_xpath + "//img"
        imageLink = BROWSER.find_element(By.XPATH, imageLink).get_attribute('src')
        log(f"Image link: {imageLink}")
        course.ImageLink = imageLink

        authorXpath = container_xpath + "//div[@class='pgn__card-header-title-md']"
        author = BROWSER.find_element(By.XPATH, authorXpath).text
        log(f"Author: {author}")
        course.Author = author

        documentXpath = container_xpath + "//span[@class='badge badge-primary']"
        document = BROWSER.find_element(By.XPATH, documentXpath).text
        log(f"Document: {document}")
        if document != "Course":
            course.Document = document
        CoursesList.append(course)
        log(" ")
    log(" ")


def getCourseInfo(Course, waitTime):
    global COURSES_PARSED
    BROWSER.get(Course.Link)
    course = copy.deepcopy(Course)

    try:
        WebDriverWait(BROWSER, waitTime).until(EC.any_of(
        EC.presence_of_element_located((By.XPATH, "(//div[@class='ml-3']/div[@class='h4 mb-0'])[last()]")),
        EC.presence_of_element_located((By.XPATH, "//div[@class='main d-flex flex-wrap']"))
                                              ))
    except:
        log(f"Error at parsing: {course.Link}")
        return False

    try:
        cheapDesign = bool(len(BROWSER.find_elements(By.XPATH, "(//div[@class='ml-3']/div[@class='h4 mb-0'])[last()]")))
        err = "cheap description"
        if cheapDesign:
            # ждём блок описания, блок длительности, блок цены. блок тегов, блок сложности, блок автора
            WebDriverWait(BROWSER, waitTime).until(EC.all_of(
                EC.presence_of_element_located((By.XPATH, "//div[@class='p']")),
                EC.presence_of_element_located((By.XPATH, "(//div[@class='ml-3']/div[@class='h4 mb-0'])[1]")),
                EC.presence_of_element_located((By.XPATH, "(//div[@class='ml-3']/div[@class='h4 mb-0'])[3]")),
                EC.presence_of_element_located((By.XPATH, "(//a[@class='muted-link inline-link'])[2]")),
                EC.presence_of_element_located((By.XPATH, "//ul[@class='mb-0 pl-3 ml-1']//span[contains(text(), 'Level')]/..")),
                EC.presence_of_element_located((By.XPATH, "//li/span[contains(text(), 'Institution')]/../a"))
            ))

            
            course.Description = BROWSER.find_element(By.XPATH, "//div[@class='p']").text

            err = "cheap duration"
            course.Duration = BROWSER.find_element(By.XPATH, "(//div[@class='ml-3']/div[@class='h4 mb-0'])[1]").text

            err = "cheap price"
            course.Price = BROWSER.find_element(By.XPATH, "(//div[@class='ml-3']/div[@class='h4 mb-0'])[3]").text
            if course.Price != "Free":
                err = "cheap price !free"
                course.Price = BROWSER.find_element(By.XPATH, "(//div[@class='ml-3']/div[@class='small'])[3]").text
            
            err = "cheap subject"
            course.Tags.append(BROWSER.find_element(By.XPATH, "(//a[@class='muted-link inline-link'])[2]").text)

            err = "cheap difficulty"
            course.Difficulty = BROWSER.find_element(By.XPATH, "//ul[@class='mb-0 pl-3 ml-1']//span[contains(text(), 'Level')]/..").text.split(": ")[1]

            err = "cheap author"
            course.Author = BROWSER.find_element(By.XPATH, "//li/span[contains(text(), 'Institution')]/../a").text
        else:
            WebDriverWait(BROWSER, waitTime).until(EC.all_of(
                EC.presence_of_element_located((By.XPATH, "//div[@class='main d-flex flex-wrap']")),
                EC.presence_of_element_located((By.XPATH, "(//div[@class='details'])[3]/div[@class='main']")),
                EC.presence_of_element_located((By.XPATH, "//div[@class='overview-info']"))
            ))
            err = "rich price"
            course.Price = BROWSER.find_element(By.XPATH, "//div[@class='main d-flex flex-wrap']").text.split("/n")[1]
            err = "rich duration"
            course.Duration = BROWSER.find_element(By.XPATH, "(//div[@class='details'])[3]/div[@class='main']").text
            err = "rich description"
            course.Description = BROWSER.find_element(By.XPATH, "//div[@class='overview-info']").text
            course.Document = "Certificate"
    except:
        log(f"Error at {err} block, {course.Link}")
        return False
    
    COURSES_PARSED = COURSES_PARSED + 1
    
    return course




def parseBegin(CoursesList):
    global PAGES_TOTAL
    global COURSES_TOTAL
    global PAGES_PARSED
    global LOG
    BROWSER.get(URL + COURSES_URL)
    COURSES_TOTAL = getCoursesTotalCount()
    PAGES_TOTAL = getPagesTotalCount()
    log(f"Courses total: {COURSES_TOTAL}")
    log(f"Pages total: {PAGES_TOTAL}")

    for page in range(2):  # заменить на range(PAGES_TOTAL)
        BROWSER.get(URL + f"/search?tab=course&page={page + 1}")
        getCoursesFromPage(CoursesList)
        PAGES_PARSED = PAGES_PARSED + 1

    log("")
    LOG = True

    # если парсинг странички курса выкинет ошибку 5 раз то прекращаем парсить курс и парсим следующий
    for course in range(len(CoursesList)): # range(len(CoursesList))
        error = 0
        # если парсинг странички курса выбросил ошибку то возвращает False, иначе - обьект course
        answer = getCourseInfo(CoursesList[course], 5)
        while answer == False and error < 5:
            log(f"{course} error {error + 1}")
            BROWSER.refresh()
            answer = getCourseInfo(CoursesList[course], 5 + error)
            error = error + 1
        if error < 5:
            CoursesList[course] = answer


def init(AllCourses, Log):
    global LOG
    LOG = Log
    print(f"Parsing {URL}")
    start = time.time()
    parseBegin(AllCourses)
    print(f"Done. {URL} parsed. Total of {COURSES_PARSED}/{COURSES_TOTAL} courses from {PAGES_PARSED}/{PAGES_TOTAL} pages. Time: {int(time.time() - start)}sec")


init([], True)
