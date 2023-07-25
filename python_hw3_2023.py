import json
import urllib.request
from web_driver import Web_Driver

def wormbaseDataCrawler(transcripID: str)-> dict:  #直接爬網頁上整理完成的資料(困難的case)
    url = "https://wormbase.org/rest/widget/transcript/" + transcripID + "/sequences"
    req = urllib.request.Request(url,headers ={"User-Agent":"Mozilla/5.0 (Xll; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"})
    with urllib.request.urlopen(req) as response:
        sequence = response.read().decode("utf-8")
    sequence: dict = json.loads(sequence)
    return sequence


def sequenceDataParser(sequence: dict)-> dict:  # 解析爬回來的資料json檔
    strand = sequence['unspliced_sequence_context_with_padding']['data']['strand']
    # 判斷正負股

    if strand == "+":
        transcriptData = sequence['unspliced_sequence_context']['data']['positive_strand']['features']
        # 將所有相關資料都儲存下來，包含位置以及序列等等
    else:
        transcriptData = sequence['unspliced_sequence_context']['data']['nagative_strand']['features']
    return transcriptData


def wormbaseSequenceCrawler(transcripID: str):  
    pass


if __name__ == "__main__":
    browser = Web_Driver(chromedriver_path="/home/cosbi2/py_project/summer_training/chromedriver_linux64/chromedriver", web_address="https://wormbase.org/species/c_elegans/transcript/Y40B10A.2a.1")
    browser.click('//*[@id="widget-transcript"]/div[1]/h3/div')
    browser.click("//button[contains(@class, 'jss49') and contains(@class, 'jss63') and contains(@class, 'jss71') and contains(@class, 'jss86') and contains(@class, 'jss62') and contains(@class, 'jss5')]")
    # wormbaseDataCrawler(transcripID="Y40B10A.2a.1")