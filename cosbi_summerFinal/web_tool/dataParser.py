import re
import urllib.request
import json
import enum
from django.http import JsonResponse


def Split_Upper(data: str) -> list:
    pattern = r"[A-Z]+"
    ExonData = re.findall(pattern, data)
    return ExonData


def Split_Lower(data: str) -> list:
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


def sequenceJsonDataParser(WBdata: dict) -> dict:  # 解析爬回來的資料json檔
    strand = WBdata["fields"]["unspliced_sequence_context_with_padding"]["data"][
        "strand"
    ]
    # 判斷正負股

    if strand == "+":
        unspliced_transcriptData = WBdata["fields"]["unspliced_sequence_context"][
            "data"
        ]["positive_strand"]["features"]
        spliced_transcriptData = WBdata["fields"]["spliced_sequence_context"]["data"][
            "positive_strand"
        ]["features"]
        # 將所有相關資料都儲存下來，包含位置以及序列等等
    else:
        unspliced_transcriptData = WBdata["fields"]["unspliced_sequence_context"][
            "data"
        ]["nagative_strand"]["features"]
        spliced_transcriptData = WBdata["fields"]["spliced_sequence_context"]["data"][
            "nagative_strand"
        ]["features"]
    return unspliced_transcriptData, spliced_transcriptData


def is_easyCase(
    unsplicedData: list, splicedData: list
) -> bool:  # 判斷兩序列的第一組小寫(5'UTR)以及最後一組小寫(3'UTR)是否相同
    return unsplicedData[0] == splicedData[0] and unsplicedData[-1] == splicedData[-1]


def difficultCaseAnswer(
    sequenceData: dict,
) -> list[tuple[int, int]]:  # 將json檔中的資料轉換儲存成能用的tuple格式
    UTR5_Result = []
    UTR3_Result = []
    IntronResult = []
    ExonResult = []
    for item in sequenceData:
        location = tuple((item["start"], item["stop"]))
        if item["type"] == "five_prime_UTR":
            UTR5_Result.append(location)
        elif item["type"] == "exon":
            ExonResult.append(location)
        elif item["type"] == "intron":
            IntronResult.append(location)
        elif item["type"] == "three_prime_UTR":
            UTR3_Result.append(location)
    return UTR5_Result, UTR3_Result, ExonResult, IntronResult


def Find_Location(sequence: str, templates: list) -> list[list[int, int]]:
    result = []
    for template in templates:
        pattern = re.compile(re.escape(template))
        MatchResult = pattern.finditer(sequence)
        for matchResult in MatchResult:
            result.append([matchResult.start() + 1, matchResult.end()])
    return result


def getTransData(request):
    target = request.Get.get("name", None)

    if target is not None:
        WBdata = wormbaseJsonCrawler(target)
        unsplicedData, splicedData = sequenceJsonDataParser(WBdata)
        if is_easyCase(unsplicedData, splicedData):
            pass
        else:
            UTR5_Result, UTR3_Result, ExonResult, IntronResult = difficultCaseAnswer(
                unsplicedData
            )
