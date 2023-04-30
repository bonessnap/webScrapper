from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from parsers.components import course_class
from parsers.components import init_browser
from parsers.components import db_connector
from parsers.components import waiter
import os
import pickle

# НЕ РАБОТАЕТ, ПРОБЕЛМА С CLOUDFARE

URL = "https://www.skillshare.com"
PLATFORM = "skillshare"
SITEMAP = "/en/sitemap/classes/1"
BROWSER = init_browser.getBrowser()

COURSES_TOTAL = 0
COURSES_PARSED = 0


LOG = False


def getCoursesLinksFromSiteMap(DBLinks):
    if os.path.exists("file.txt"):
        with open("file.txt", 'rb') as f:
            links = pickle.load(f)
            return links
    
    try:
        BROWSER.get(URL + SITEMAP)
        html = BROWSER.page_source
        soup = BeautifulSoup(html, "lxml")   
        links = [link.text for link in soup.find_all('loc') if not link.text in DBLinks]
    except: 
        return False
    
    if not os.path.exists("file.txt"):
        with open("file.txt", 'ab') as f:
            pickle.dump(links, f)
    return links


def getCourseFromLink(Link):
    BROWSER.get(Link)
    titles = BROWSER.find_elements(By.XPATH, "//span[@class='title']")
    if len(titles)!=0:
        print(f"Titles: {titles[0].text}")
    else:
        print("Error, no title")

def parseBegin(DBLinks):
    global BROWSER
    # обход CloudFare не работает
    BROWSER.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    'source': '''
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        '''
    })
    BROWSER.get(URL)
    links = False
    errors_left = 5
    while links == False and errors_left != 0:
        errors_left = errors_left - 1
        links = getCoursesLinksFromSiteMap(DBLinks)
    if links == False:
        return 
    
    print(f"Links: {len(links)}")
    for i in range(20):
        print(f"Link[{i}]: {links[i]}")
        getCourseFromLink(links[i])
    


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
