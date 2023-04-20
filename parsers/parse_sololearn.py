from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import time
from parsers.components import course_class
from parsers.components import init_browser

# РАБОТАЕТ #

Courses = []

URL = "https://www.sololearn.com"


def parseBegin():
    browser = init_browser.getBrowser()

    # открываем сайт
    browser.get(URL + "/learn")
    # получаем код странички
    html = browser.page_source
    # превращаем его в БС обьект
    soup = BeautifulSoup(html, "html.parser")
    # Находим контейнер с тегами и оттуда теги
    tags = soup.find(
        'div', class_='sl-categorized-courses__container').find('div', class_='sl-horizontal')
    # теги
    tags = tags.find_all('div', class_='sl-horizontal__item')[1:]
    # xpath пути к кнопкам для вызова функции нажатия категории по xpath
    Xpathes = []
    # превращаем теги из html в текст и создаем пути
    for i in range(len(tags)):
        tags[i] = tags[i].text
        xpath = '//*[@id="main"]/div/main/main/div/section/div/div[1]/div/div[' + \
            str(i + 2) + ']/button'
        Xpathes.append(xpath)

    global Courses

    # находим все контейнеры с описанием курсов
    containers = soup.find_all('a', class_="le-course-item-v3")
    # проходимся по списку ВСЕХ курсов и собираем инфу
    for container in range(len(containers)):
        course = course_class.getCourse()
        # сначала парсим поля
        course.Title = containers[container].find(
            'p', class_="le-course-item-v3__title").text
        course.ImageLink = containers[container].find(
            'div', class_='le-course-item-v3__icon').find('img')['src']
        course.Description = containers[container].find(
            'p', class_='le-course-item-v3__description').text
        course.Link = URL + containers[container]['href']

        # поля по-умолчанию
        course.Price = "Free"
        course.Author = "Sololearn"
        course.Document = "Certificate"
        Courses.append(course)
        # дебаг выводит в консоль фулл инфу о каждом курсе
        # print("Курс:",(container+1))
        # course.printSelf()
        # print()

    # проходимся по тегам по их xpath
    # поскольку на сайте открывается тег и в нем спиок курсов
    # открываем каждый тег и смотрим какие в нём есть курсы
    # если в этом теге есть курс из списка курсов, то в его теги добавляет тег
    for xpath in range(len(Xpathes)):
        button = browser.find_element(By.XPATH, Xpathes[xpath])
        browser.execute_script("arguments[0].click();", button)
        html = browser.page_source
        soup = BeautifulSoup(html, "html.parser")
        containers = soup.find_all('a', class_="le-course-item-v3")
        for container in range(len(containers)):
            for course in range(len(Courses)):
                if Courses[course].Title == containers[container].find('p', class_="le-course-item-v3__title").text:
                    Courses[course].Tags.append(tags[xpath])

    browser.quit()


def init(AllCourses):
    print(f"Parsing {URL}")
    start = time.time()
    parseBegin()
    print(f"Done. {URL} parsed. Total of {len(Courses)} courses. Time: {int(time.time() - start)}sec")
    AllCourses.extend(Courses)
