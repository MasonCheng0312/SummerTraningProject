import json
import os
import pandas as pd
import urllib.request
from web_driver import Web_Driver
from python_hw2_2022 import Parse_File, Split_Lower, Split_Upper, Find_Location, DataName

def wormbaseAnswerCrawler(transcripID: str)-> dict:  #直接爬網頁上整理完成的資料(困難的case)
    url = "https://wormbase.org/rest/widget/transcript/" + transcripID + "/sequences"
    req = urllib.request.Request(url,headers ={"User-Agent":"Mozilla/5.0 (Xll; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"})
    with urllib.request.urlopen(req) as response:
        sequence = response.read().decode("utf-8")
    sequence: dict = json.loads(sequence)
    return sequence


def sequenceDataParser(sequence: dict)-> dict:  # 解析爬回來的資料json檔
    strand = sequence['fields']['unspliced_sequence_context_with_padding']['data']['strand']
    # 判斷正負股

    if strand == "+":
        unspliced_transcriptData = sequence['fields']['unspliced_sequence_context']['data']['positive_strand']['features']
        spliced_transcriptData = sequence['fields']["spliced_sequence_context"]['data']['positive_strand']['features']
        # 將所有相關資料都儲存下來，包含位置以及序列等等
    else:
        unspliced_transcriptData = sequence['fields']['unspliced_sequence_context']['data']['nagative_strand']['features']
        spliced_transcriptData = sequence['fields']["spliced_sequence_context"]['data']['nagative_strand']['features']
    return unspliced_transcriptData, spliced_transcriptData


def wormbaseSequenceFileCrawler(transcripID: str)-> bool:  # 爬蟲下載切割與未切割的序列檔案，回傳是否成功下載的布林值
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

def check_case(unsplicedData: list, splicedData: list) -> bool:  # 判斷兩序列的第一組小寫(5'UTR)以及最後一組小寫(3'UTR)是否相同
    return unsplicedData[0] == splicedData[0] and unsplicedData[-1] == splicedData[-1]


def Split_dict_to_tuple(data: list[dict[str, tuple[int, int]]]):  # 將舊的檔案格式更改為較為簡單的tuple形式
    result = []
    for _, data_dict in enumerate(sorted(data, key=lambda x: list(x.values())[0][0])):
        location = list(data_dict.values())
        startPoint = location[0][0]
        endPoint = location[0][1]
        result.append(tuple((startPoint, endPoint)))
    return result

def Append_TO_Dataframe(dataframe: pd.DataFrame, data: list[tuple[int, int]], flag: int):  # 將資料匯入DataFrame中儲存成欲輸出的格式
    for item in data:
        if flag >= 3:
            data_name = str(DataName(flag).name)
        else:
            data_name = str(DataName(flag).name) + f'{data.index(item)+ 1}'        
        length = item[1] - item[0] + 1
        dataframe.loc[len(dataframe)] = {'名稱': data_name, '起始位置': item[0], '結束位置': item[1], '長度': length}
    return dataframe

def sequenceData_to_tuple(sequenceData):  # 將json檔中的資料轉換儲存成能用的tuple格式
    UTR5_Result = []
    UTR3_Result = []
    IntronResult = []
    ExonResult = []
    for item in sequenceData:
        location = tuple((item["start"], item["stop"]))
        if item["type"] == "five_prime_UTR":
            UTR5_Result.append(location)
        elif item["type"] == 'exon':
            ExonResult.append(location)
        elif item["type"] == 'intron':
            IntronResult.append(location)
        elif item["type"] == 'three_prime_UTR':
            UTR3_Result.append(location)
    return UTR5_Result, UTR3_Result, ExonResult, IntronResult


def split_Data(ParseData):  # 舊版的資料處裡時需要更改成正確的序列位置
    Exon = Split_Upper(str(ParseData))
    UTR_And_Intron = Split_Lower(str(ParseData))
    ExonResult = Find_Location(ParseData, Exon)
    IntronResult = Find_Location(str(ParseData), UTR_And_Intron)
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


def cds_finder(UTR5, UTR3, Exon):  # 找到CDS的位置
    cds = []
    if len(UTR5) != 0:
        start_pt = int(UTR5[-1][1]) + 1
    else:
        start_pt = 1
    if len(UTR3) != 0:
        end_pt = int(UTR3[0][0]) - 1
    else:
        end_pt = Exon[-1][1]
    cds.append(tuple((start_pt, end_pt)))
    return cds    


if __name__ == "__main__":
    search_target = input("please enter the target transcriptID you want to search\n")
    if wormbaseSequenceFileCrawler(transcripID=search_target) : # 是否成功爬蟲(if yes)
        unsplicedSequence = Parse_File("/home/cosbi2/py_project/summer_training/unspliced+UTRTranscriptSequence_"+ search_target + ".fasta")
        splicedSequence = Parse_File("/home/cosbi2/py_project/summer_training/spliced+UTRTranscriptSequence_"+ search_target + ".fasta")
        unsplicedIntron = Split_Lower(unsplicedSequence[0])
        splicedIntron = Split_Lower(splicedSequence[0])
        functionFlag = check_case(unsplicedIntron, splicedIntron)
    else:
        functionFlag = False
    if functionFlag:
        ExonResult, IntronResult, UTR5_Result, UTR3_Result = split_Data(unsplicedSequence[0])
        Dataframe = pd.DataFrame(columns=['名稱', '起始位置', '結束位置', '長度'])
        Dataframe = Append_TO_Dataframe(Dataframe, Split_dict_to_tuple(UTR5_Result), 3)
        Dataframe = Append_TO_Dataframe(Dataframe, Split_dict_to_tuple(UTR3_Result), 4)
        Dataframe = Append_TO_Dataframe(Dataframe, Split_dict_to_tuple(IntronResult), 2)
        Dataframe = Append_TO_Dataframe(Dataframe, Split_dict_to_tuple(ExonResult), 1)
        Dataframe = Dataframe.sort_values('起始位置')
        Dataframe.to_csv(search_target + "_result.csv", index=False)
    else:
        detail_data = wormbaseAnswerCrawler(search_target)
        unspliced_result, spliced_result= sequenceDataParser(detail_data)
        UTR5_Result, UTR3_Result, ExonResult, IntronResult = sequenceData_to_tuple(unspliced_result)
        Dataframe = pd.DataFrame(columns=['名稱', '起始位置', '結束位置', '長度'])
        Dataframe = Append_TO_Dataframe(Dataframe, UTR5_Result, 3)
        Dataframe = Append_TO_Dataframe(Dataframe, UTR3_Result, 4)
        Dataframe = Append_TO_Dataframe(Dataframe, IntronResult, 2)
        Dataframe = Append_TO_Dataframe(Dataframe, ExonResult, 1)
        Dataframe = Dataframe.sort_values('起始位置')        
        Dataframe.to_csv(search_target + "_unspliced_result.csv", index=False)

        Dataframe.drop(Dataframe.index, inplace=True)
        # 清空dataframe但保留標頭
        UTR5_Result, UTR3_Result, ExonResult, _ = sequenceData_to_tuple(spliced_result)
        CDS_Result = cds_finder(UTR5_Result, UTR3_Result, ExonResult)
        Dataframe = Append_TO_Dataframe(Dataframe, UTR5_Result, 3)
        Dataframe = Append_TO_Dataframe(Dataframe, CDS_Result, 5)
        Dataframe = Append_TO_Dataframe(Dataframe, UTR3_Result, 4)
        Dataframe = Append_TO_Dataframe(Dataframe, ExonResult, 1)   
        Dataframe.to_csv(search_target + "_spliced_result.csv", index=False)

    os.remove("/home/cosbi2/py_project/summer_training/unspliced+UTRTranscriptSequence_"+ search_target + ".fasta")
    os.remove("/home/cosbi2/py_project/summer_training/spliced+UTRTranscriptSequence_"+ search_target + ".fasta")