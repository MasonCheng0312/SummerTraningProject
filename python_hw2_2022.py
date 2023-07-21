import re
from enum import Enum
import pandas as pd
import time

def Parse_File(file_path: str):
    data = []
    file = open(file_path)
    for readline in file:
        if readline.startswith(">") == False:
            data.append(readline)
    return data


def Split_Upper(data: str):
    pattern = r'[A-Z]+'
    ExonData = re.findall(pattern, data)
    return ExonData


def Split_Lower(data: str) -> list:
    pattern = r'[a-z]+'
    Intron_And_UTR_Data = re.findall(pattern, data)
    return Intron_And_UTR_Data


def Find_Location(data: str, templates: list) -> list[dict[str, tuple[int, int]]]:
    result = []
    for template in templates:
        pattern = re.compile(re.escape(template))
        MatchResult = pattern.finditer(data)
        for matchResult in MatchResult:
            result.append({matchResult.group(): (matchResult.start() + 1, matchResult.end())})
    return result


class DataName(Enum):
    Exon = 1
    Intron = 2
    UTR5 = 3
    UTR3 = 4
    CDS = 5


def Append_TO_Dataframe(dataframe: pd.DataFrame, data: list[dict[str, tuple[int, int]]], flag: int):
    for index, data_dict in enumerate(sorted(data, key=lambda x: list(x.values())[0][0])):
        if flag >= 3:
            data_name = str(DataName(flag).name)
        else:
            data_name = str(DataName(flag).name) + f'{index + 1}'
        location = list(data_dict.values())
        startPoint = location[0][0]
        endPoint = location[0][1]
        length = endPoint - startPoint + 1
        dataframe.loc[len(dataframe)] = {'名稱': data_name, '起始位置': startPoint, '結束位置': endPoint, '長度': length}
    return dataframe


def main():
    start = time.perf_counter()
    Path = "unspliced+UTRTranscriptSequence_Y40B10A.2a.1.fasta" 
    ParseData = Parse_File(Path)
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
    
    print(ExonResult)
    # intron的第一個是UTR5，最後一個是UTR3，我們不要。

    
    Dataframe = pd.DataFrame(columns=['名稱', '起始位置', '結束位置', '長度'])
    Dataframe = Append_TO_Dataframe(Dataframe, UTR5_Result, 3)
    Dataframe = Append_TO_Dataframe(Dataframe, UTR3_Result, 4)
    Dataframe = Append_TO_Dataframe(Dataframe, IntronResult, 2)
    Dataframe = Append_TO_Dataframe(Dataframe, ExonResult, 1)


    Dataframe = Dataframe.sort_values('起始位置')
    # 根據"起始位置"欄位的值做排序。
    
    Dataframe.to_csv("hw2_result.csv", index=False)
    
    end = time.perf_counter()
    print( end-start )

if __name__ == "__main__":
    main()
