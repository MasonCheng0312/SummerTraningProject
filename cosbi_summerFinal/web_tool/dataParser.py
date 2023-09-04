import re
import urllib.request
import json
from enum import Enum
from django.http import JsonResponse


class DataType(Enum):
    Utr5 = "5'UTR"
    Utr3 = "3'UTR"
    Exon = "Exon"
    Intron = "Intron"
    CDS = "CDS"


def Split_Upper(data: str) -> list[str]:
    pattern = r"[A-Z]+"
    ExonData = re.findall(pattern, data)
    return ExonData


def Split_Lower(data: str) -> list[str]:
    pattern = r"[a-z]+"
    Intron_And_UTR_Data = re.findall(pattern, data)
    return Intron_And_UTR_Data


def wormbaseJsonCrawler(transcripID: str) -> dict:
    url = "https://wormbase.org/rest/widget/transcript/" + transcripID + "/sequences"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Xll; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
        },
    )
    with urllib.request.urlopen(req) as response:
        sequence = response.read().decode("utf-8")
    sequence: dict = json.loads(sequence)
    return sequence


def sequenceJsonDataParser(WBdata: dict) -> tuple[dict, dict]:  # 解析爬回來的資料json檔
    strand = WBdata["fields"]["unspliced_sequence_context_with_padding"]["data"][
        "strand"
    ]
    # 判斷正負股

    if strand == "+":
        unspliced_transcriptData = WBdata["fields"]["unspliced_sequence_context"][
            "data"
        ]["positive_strand"]
        spliced_transcriptData = WBdata["fields"]["spliced_sequence_context"]["data"][
            "positive_strand"
        ]
        # 將所有相關資料都儲存下來，包含位置以及序列等等
    else:
        unspliced_transcriptData = WBdata["fields"]["unspliced_sequence_context"][
            "data"
        ]["negative_strand"]
        spliced_transcriptData = WBdata["fields"]["spliced_sequence_context"]["data"][
            "negative_strand"
        ]
    return unspliced_transcriptData, spliced_transcriptData


def is_easyCase(
    unsplicedData: list, splicedData: list
) -> bool:  # 判斷兩序列的第一組小寫(5'UTR)以及最後一組小寫(3'UTR)是否相同
    return unsplicedData[0] == splicedData[0] and unsplicedData[-1] == splicedData[-1]


def difficultCaseAnswer(
    sequenceData: dict,
) -> list[list[tuple[int, int], DataType]]:  # 將json檔中的資料轉換儲存成能用的tuple格式
    UTR5_Result = []
    UTR3_Result = []
    IntronResult = []
    ExonResult = []
    for item in sequenceData["features"]:
        location = tuple((item["start"], item["stop"]))
        if item["type"] == "five_prime_UTR":
            UTR5_Result.append(location)
        elif item["type"] == "exon":
            ExonResult.append(location)
        elif item["type"] == "intron":
            IntronResult.append(location)
        elif item["type"] == "three_prime_UTR":
            UTR3_Result.append(location)
        sortedData = [
            [UTR5_Result, DataType.Utr5],
            [UTR3_Result, DataType.Utr3],
            [ExonResult, DataType.Exon],
            [IntronResult, DataType.Intron],
        ]
    return sortedData


def easyCaseAnswer(unsplicedSeq, splicedSeq) -> list[list[tuple[int, int], DataType]]:
    def ExonRefactoring(Exon:list[str],  Utr_Intron:list[str]) -> list[str]:
        # in easy case, Exon1 contain 5'UTR, and last Exon contain 3'UTR.
        Exon[0] = Utr_Intron[0] + Exon[0]
        Exon[-1] = Exon[-1] + Utr_Intron[-1]
        return Exon
    

    def Find_Location(sequence: str, templates: list) -> list[tuple[int, int]]:
        result = []
        for template in templates:
            pattern = re.compile(re.escape(template))
            matchResult = pattern.search(sequence)
            if matchResult:
                result.append(tuple((matchResult.start() + 1, matchResult.end())))
        return result
    

    def getResult(resultList:list, ExonLoc:list[tuple[(int, int)]], IntronAndUtrLoc:list[tuple[int, int]]):
        resultList.append([ExonLoc, DataType.Exon])       
        resultList.append([IntronAndUtrLoc[1:-1], DataType.Intron])
        resultList.append([[IntronAndUtrLoc[0]], DataType.Utr5])
        resultList.append([[IntronAndUtrLoc[-1]], DataType.Utr3])
        return resultList
    
    unsplicedResult = []
    splicedResult = []
    Exon = Split_Upper(unsplicedSeq)
    Utr_Intron = Split_Lower(unsplicedSeq)
    Exon = ExonRefactoring(Exon, Utr_Intron)

    unsplicedExonLoc = Find_Location(unsplicedSeq, Exon)
    splicedExonLoc = Find_Location(splicedSeq, Exon)
    
    unsplicedIntronAndUtrLoc = Find_Location(unsplicedSeq, Utr_Intron)
    Utr = Split_Lower(splicedSeq)
    splicedUtrLoc = Find_Location(splicedSeq, Utr)

    unsplicedData = getResult(unsplicedResult, unsplicedExonLoc, unsplicedIntronAndUtrLoc)
    splicedData = getResult(splicedResult, splicedExonLoc, splicedUtrLoc)
    return unsplicedData, splicedData


def getCDSInfo(AssortedData):
    Utr3 = []
    Utr5 = []
    for item in AssortedData:
        if item[1] == DataType.Exon:
            ExonLoc = item[0]
        elif item[1] == DataType.Utr3:
            Utr3 = item[0]
        elif item[1] == DataType.Utr5:
            Utr5 = item[0]
    if Utr5:
        start_pt = int(Utr5[-1][1]) + 1
    else:
        start_pt = 1
    if Utr3:
        end_pt = int(Utr3[0][0]) - 1
    else:
        end_pt = ExonLoc[-1][1]

    return [[tuple((start_pt, end_pt))], DataType.CDS]


def responseOperater(AssortedData:list[list[tuple[int, int], DataType]]):
    response = []
    for item in AssortedData:
        if (item[1] == DataType.Exon) or (item[1] == DataType.Intron):
            for index, location in enumerate(item[0]):
                result = {
                    "start_point":location[0],
                    "end_point":location[1],
                    "name":item[1].value + str(index + 1),
                          }
                response.append(result)
        else:
            for location in item[0]:
                result = {
                    "start_point":location[0],
                    "end_point":location[1],
                    "name":item[1].value,
                          }
                response.append(result)
    print(response)            
    return response

def getTransData(request):
    target = request.GET.get("name", None)

    if target is not None:
        WBdata = wormbaseJsonCrawler(target)
        unsplicedData, splicedData = sequenceJsonDataParser(WBdata)
        unsplicedSequence = unsplicedData['sequence']
        splicedSequence = splicedData['sequence']
        intronInUnsplicedData = Split_Lower(unsplicedSequence)
        intronInSplicedData = Split_Lower(splicedSequence)
        if is_easyCase(intronInUnsplicedData, intronInSplicedData):
            unsplicedAssortedData, splicedAssortedData= easyCaseAnswer(unsplicedSequence, splicedSequence)       
            splicedAssortedData.append(getCDSInfo(splicedAssortedData))
        else:
            unsplicedAssortedData = difficultCaseAnswer(unsplicedData)
            splicedAssortedData = difficultCaseAnswer(splicedData)
            splicedAssortedData.append(getCDSInfo(splicedAssortedData))
        response = {"unsplicedData":responseOperater(unsplicedAssortedData),
                    "unsplicedSeq":unsplicedSequence,
                    "splicedData":responseOperater(splicedAssortedData),
                    "splicedSeq":splicedSequence,}
    return JsonResponse(response, safe=False)



        

