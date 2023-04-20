
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# тут создается обьект браузер с настройками и возвращается в парсер
def getBrowser():
    # настройки браузера
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")
    # без открытия окна (тихий режим)
    chrome_options.add_argument("--headless")
    # без логирования
    chrome_options.add_argument("--disable-logging")
    # без трассировки
    chrome_options.add_argument("--disable-in-process-stack-traces")
    # без крашрепорта
    chrome_options.add_argument("--disable-crash-reporter")
    # разрешить жс
    chrome_options.add_argument("--enable-javascript")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_experimental_option(
        'excludeSwitches', ['enable-logging'])
    chrome_options.add_argument('--disable-extensions')
  
    BROWSER = webdriver.Chrome(options=chrome_options)
    return BROWSER