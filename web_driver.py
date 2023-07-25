from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time


class Web_Driver():
    def __init__(self, chromedriver_path: str, web_address: str):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--mute-audio")
        # 將網頁靜音
        # self.chrome_options.add_argument("--headless")
        # 將網頁設定在後台運行，不會彈出視窗
        self.chrome_options.add_argument("--disable-gpu")
        # 禁止使用gpu加速，提高爬蟲的穩定性
        self.chrome_options.add_argument("--detach=true")
        #　在程式結束後不關閉網頁
        self.chrome_options.add_argument("--download.default_directory=/home/cosbi2/py_project/summer_training")
        self.browser = webdriver.Chrome(options=self.chrome_options, executable_path=chromedriver_path)
        self.browser.get(web_address)
        time.sleep(5)
    
    def click(self, xpath):
        print(type(self.browser))
        elements = self.find_element(By.XPATH, xpath)
        print(elements)
        print(type(elements))
        elements[0].click()
        
    def quit(self):
        self.browser.quit()