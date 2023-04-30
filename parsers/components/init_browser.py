from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def getBrowser():
    # Настройки браузера
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--headless") # Режим без открытия окна (тихий режим)
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--disable-in-process-stack-traces")
    chrome_options.add_argument("--disable-crash-reporter")
    chrome_options.add_argument("--enable-javascript")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--no-sandbox") # Для безопасности в режиме headless
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument("--disable-extensions")
  
    try:
        # Создание объекта браузера
        browser = webdriver.Chrome(options=chrome_options)
        return browser
    except:
        print("Failed to create browser instance!")
        return None
