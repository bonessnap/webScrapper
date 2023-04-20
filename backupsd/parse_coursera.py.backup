from bs4 import BeautifulSoup
import course_class
import time
import init_browser
from selenium.webdriver.common.by import By

URL = "https://www.coursera.org"
BROWSER = init_browser.getBrowser()
COURSES = []
PAGES_PARSED = 0
LOG = False

# дебаг функция, которая принимает строку и если parse_coursera.init
def log(string):
    if LOG:
        print(string)


def parsePage(html):
    global COURSES
    soup = BeautifulSoup(html, "html.parser")
    containers = []
    for i in soup.find_all('div', class_=['css-1pa69gt','css-1j8ushu']):
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
            author = upperBlock.find('span', class_=['cds-33','css-2fzscr','cds-35']).text
            course.Author = author
            log(f"Author: {author}")
            title = upperBlock.find('h2').text
            course.Title = title
            log(f"Title: {title}") 
            tags = upperBlock.find('p', class_=['cds-33','css-5or6ht','cds-35'])
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

            lastInfoBlock = datablock.find_all('p', class_=['cds-33','css-14d8ngk','cds-35'])[-1]
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
        COURSES.append(course)
        log("")


def parseBegin():
    global PAGES_PARSED
    BROWSER.get(URL + "/courses")
    time.sleep(5)    
    soup = BeautifulSoup(BROWSER.page_source, "html.parser")
    pages_total = int(soup.find_all('div', class_=['rc-PaginationControls','horizontal-box','align-items-right','large-style','cds','css-k2t558'])[-1].text[5:])
    log(f"Pages: {pages_total}")    
    log(f"Page: {1}")
    html = BROWSER.page_source
    BROWSER.find_element(By.XPATH, "(//button[contains(@class, 'arrow')])[last()]").click()
    parsePage(html)
    PAGES_PARSED = PAGES_PARSED + 1

    # проходимся по каждой странице и вытягиваем курсы
    for i in range(1, 3):
        time.sleep(2)
        log(f"Page: {(i+1)}")
        html = BROWSER.page_source
        BROWSER.find_element(By.XPATH, "(//button[contains(@class, 'arrow')])[last()]").click()
        parsePage(html)
        PAGES_PARSED = PAGES_PARSED + 1
        log("\n\n")

    BROWSER.close()
    BROWSER.quit()


def init(AllCourses, log):
    global LOG
    LOG = log
    print(f"Parsing {URL}")
    start = time.time()
    parseBegin()
    print(f"Done. {URL} parsed. Total of {len(COURSES)} courses form {PAGES_PARSED} pages. Time: {int(time.time() - start)}sec")
    AllCourses.extend(COURSES)
