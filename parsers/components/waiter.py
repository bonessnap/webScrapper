from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

Methods = []

def setXpathes(xpathes):
    global Methods
    Methods = []
    for i in xpathes:
        Methods.append(EC.presence_of_element_located((By.XPATH, i)))


def waitAll(Browser, WaitTime, Xpathes):
    setXpathes(Xpathes)
    try:
        WebDriverWait(Browser, WaitTime).until(waitForAllElements(Methods))
    except:
        return False
    return True


def waitOne(Browser, WaitTime, Xpathes):
    setXpathes(Xpathes)
    try:
        WebDriverWait(Browser, WaitTime).until(waitForOneElement(Methods))
    except:
        return False
    return True


class waitForAllElements(object):
    def __init__(self, methods):
        self.methods = methods

    def __call__(self, driver):
        try:
            for method in self.methods:
                if not method(driver):
                    return False
            return True
        except:
            return False
        
        
class waitForOneElement(object):
    def __init__(self, methods):
        self.methods = methods

    def __call__(self, driver):
        try:
            for method in self.methods:
                if method(driver):
                    return True
            return False
        except:
            return False