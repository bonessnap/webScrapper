from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import time
from parsers.components import course_class
from parsers.components import init_browser
from parsers.components import db_connector

# РАБОТАЕТ #

Courses = []

URL = "https://www.sololearn.com"
PLATFORM = "sololearn"


def parseBegin(DBLinks):
    browser = init_browser.getBrowser()

    browser.get(URL + "/learn")
    html = browser.page_source
    soup = BeautifulSoup(html, "html.parser")
    tags = soup.find('div', class_='sl-categorized-courses__container').find('div', class_='sl-horizontal')
    tags = tags.find_all('div', class_='sl-horizontal__item')[1:]
    
    Xpathes = []
    for i in range(len(tags)):
        tags[i] = tags[i].text
        xpath = '//*[@id="main"]/div/main/main/div/section/div/div[1]/div/div[' + str(i + 2) + ']/button'
        Xpathes.append(xpath)
    global Courses

    containers = soup.find_all('a', class_="le-course-item-v3")
    for container in range(len(containers)):
        if URL + containers[container]['href'] in DBLinks:
            continue
        course = course_class.getCourse()
        course.Title = containers[container].find('p', class_="le-course-item-v3__title").text
        course.ImageLink = containers[container].find('div', class_='le-course-item-v3__icon').find('img')['src']
        course.Description = containers[container].find('p', class_='le-course-item-v3__description').text
        course.Link = URL + containers[container]['href']
        course.Price = "Free"
        course.Author = "Sololearn"
        course.Document = "Certificate"
        course.Platformlink = URL
        course.PlatformName = PLATFORM
        Courses.append(course)

    for xpath in range(len(Xpathes)):
        button = browser.find_element(By.XPATH, Xpathes[xpath])
        browser.execute_script("arguments[0].click();", button)
        html = browser.page_source
        soup = BeautifulSoup(html, "html.parser")
        containers = soup.find_all('a', class_="le-course-item-v3")
        for container in range(len(containers)):
            if URL + containers[container]['href'] in DBLinks:
                continue
            for course in range(len(Courses)):
                if Courses[course].Title == containers[container].find('p', class_="le-course-item-v3__title").text:
                    Courses[course].Tags.append(tags[xpath])

    browser.quit()
    db_connector.insertCoursesListToDB(Courses)


def init():
    print(f"Parsing {URL}")
    DBLinks = db_connector.getCoursesLinksByPlatformName(PLATFORM)
    start = time.time()
    parseBegin(DBLinks)
    print(f"Done. {URL} parsed with {len(Courses)} courses. Total of {len(Courses) + len(DBLinks)} courses in database. Time: {int(time.time() - start)}sec")
