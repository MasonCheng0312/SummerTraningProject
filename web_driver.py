from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time


class Web_Driver():
    def __init__(self, chromedriver_path: str, web_address: str):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--mute-audio")
        # 將網頁靜音
        self.chrome_options.add_argument("--headless")
        # 將網頁設定在後台運行，不會彈出視窗
        self.chrome_options.add_argument("--disable-gpu")
        # 禁止使用gpu加速，提高爬蟲的穩定性
        self.chrome_options.add_argument("--detach=true")
        # 在程式結束後不關閉網頁
        self.chrome_options.add_experimental_option("prefs", {"download.default_directory": "/home/cosbi2/py_project/summer_training"})
        # 改變預設下載路徑
        service = Service(executable_path=chromedriver_path)
        self.browser = webdriver.Chrome(options=self.chrome_options, service=service)
        self.browser.get(web_address)
        time.sleep(4.5)
        for _ in range(2):
            self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(1.5)
    
    def click(self, xpath):
        elements = self.browser.find_element(By.XPATH, xpath)
        elements.click()
        time.sleep(0.5)
        
    def quit(self):
        self.browser.quit()
        time.sleep(1.5)