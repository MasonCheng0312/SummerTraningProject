import json
import pandas as pd
import urllib.request
from web_driver import Web_Driver
from python_hw2_2022 import Parse_File, Split_Lower, Split_Upper, Append_TO_Dataframe, Find_Location,DataName

def wormbaseAnswerCrawler(transcripID: str)-> dict:  #直接爬網頁上整理完成的資料(困難的case)
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


def wormbaseSequenceFileCrawler(transcripID: str)-> bool:
    web_address  = "https://wormbase.org/species/c_elegans/transcript/" + transcripID
    browser = Web_Driver(chromedriver_path="/home/cosbi2/py_project/summer_training/chromedriver_linux64/chromedriver", web_address=web_address)
    try:    
        browser.click('/html/body/div[2]/div[3]/div[3]/div[2]/div[1]/li[12]/div/div[2]/div[2]/div[1]/div[2]/div/div/div[1]/div/button[2]')
        browser.click("/html/body/div[2]/div[3]/div[3]/div[2]/div[1]/li[12]/div/div[2]/div[2]/div[1]/div[2]/div/div/div[2]/div/button[2]")
        browser.quit()
        flag = True
    except:
        browser.quit()
        flag = False
    return flag

def check_case(unsplicedData: list, splicedData: list) -> bool:
    return unsplicedData[0] == splicedData[0] and unsplicedData[-1] == splicedData[-1]


def splitData(ParseData):
    Exon = Split_Upper(str(ParseData[0]))
    UTR_And_Intron = Split_Lower(str(ParseData[0]))
    ExonResult = Find_Location(ParseData[0], Exon)
    IntronResult = Find_Location(str(ParseData[0]), UTR_And_Intron)

    UTR5_Result = [IntronResult[0]]
    UTR3_Result = [IntronResult[-1]]
    # 此處將Intron資料中的UTR資料分別取出。
    Exonkey = list(ExonResult[0].keys())
    # 將Exon1的資料提出，並將Exon1的Key存到Exonkey中。
    exonLocation = list(ExonResult[0][Exonkey[0]])
    # 將上一行得到的Key丟到dict中得到value，即為存有位置資料的tuple，但因為tuple不能改，我們直接強制轉型別成list。

    UTR5key = list(UTR5_Result[0].keys())    
    # 對UTR5也同理。
    utr5Location = list(UTR5_Result[0][UTR5key[0]])
    exonLocation[0] = utr5Location[0]
    # 跟Exon1的起始位置更改為UTR5的起始位置。
    ExonResult.pop(0)
    # 將原始Exon1資料刪除。
    ExonResult.append({str(Exonkey[0]) : (exonLocation[0], exonLocation[1])})
    # 將新的資料匯入ExonResult資料list。
    Exonkey = list(ExonResult[-2].keys())
    # 同上，由於剛剛用了append，原本最後一筆資料是Exon4，但現在變成了剛剛新增的Exon1，故我們找倒數第二個，即-2。
    exonLocation = list(ExonResult[-2][Exonkey[0]])
    UTR3key = list(UTR3_Result[0].keys())
    utr3Location = list(UTR3_Result[0][UTR3key[0]])
    exonLocation[1] = utr3Location[1]
    # 注意，與剛剛不同，此處應修改的是RNA的"中止位置"。
    ExonResult.pop(-2)
    ExonResult.append({str(Exonkey[0]) : (exonLocation[0], exonLocation[1])})    
    IntronResult = IntronResult[1 : -1]

    return ExonResult, IntronResult, UTR5_Result, UTR3_Result

if __name__ == "__main__":
    search_target = input("please enter the target transcriptID you want to search\n")
    if wormbaseSequenceFileCrawler(transcripID=search_target) :
        unsplicedSequence = Parse_File("unspliced+UTRTranscriptSequence_"+ search_target + ".fasta")
        splicedSequence = Parse_File("spliced+UTRTranscriptSequence_"+ search_target + ".fasta")
        unsplicedIntron = Split_Lower(unsplicedSequence[0])
        splicedIntron = Split_Lower(splicedSequence[0])
        functionFlag = check_case(unsplicedIntron, splicedIntron)
    else:
        functionFlag = False

    if functionFlag:
        ExonResult, IntronResult, UTR5_Result, UTR3_Result = splitData(unsplicedSequence[0])
        Dataframe = pd.DataFrame(columns=['名稱', '起始位置', '結束位置', '長度'])
        Dataframe = Append_TO_Dataframe(Dataframe, UTR5_Result, 3)
        Dataframe = Append_TO_Dataframe(Dataframe, UTR3_Result, 4)
        Dataframe = Append_TO_Dataframe(Dataframe, IntronResult, 2)
        Dataframe = Append_TO_Dataframe(Dataframe, ExonResult, 1)
        Dataframe.to_csv("hw5_result.csv", index=False)
    else:
        detail_data = wormbaseAnswerCrawler(search_target)
        result = sequenceDataParser(detail_data)
        print(result)