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


def answerParser(
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


def getCDSInfo(splicedSeq: str) -> list[tuple[int, int], DataType] :
    def Find_Location(sequence: str, templates: list) -> list[tuple[int, int]]:
        result = []
        for template in templates:
            pattern = re.compile(re.escape(template))
            matchResult = pattern.search(sequence)
            if matchResult:
                result.append(tuple((matchResult.start() + 1, matchResult.end())))
        return result
   
    CDS_seq = Split_Upper(splicedSeq)
    location = Find_Location(splicedSeq, CDS_seq)
    start_pt = location[0][0]
    end_pt = location[0][1]
    return [[tuple((start_pt, end_pt))], DataType.CDS]


def getProteinInfo(CDS) -> str:
    def load_codon_table():
        with open("data/codon_table.json", "r") as file:
            codon_table_data = json.load(file)
        return codon_table_data

    codon_table = load_codon_table()
    cds_sequence = CDS.replace("T", "U")
    # 從檔案中得到的資料是DNA的ATCG含氮鹼基，須將T轉換成U才是能夠轉譯的RNA序列。
    unit_set: list = [cds_sequence[i : i + 3] for i in range(0, len(cds_sequence), 3)]
    # 將cds的序列每三個鹼基做切割並存入list中。
    
    unitProtein: list = [codon_table[unit] for unit in unit_set]
    # 將切割完成的單元作為輸入找到在codon_table中的對應的胺基酸。
    unitProtein.pop(unitProtein.index("STOP"))
    # 將結果中代表中止的STOP訊號從胺基酸序列中刪除。
    proteinSeq = "".join(unitProtein)

    return proteinSeq


def responseOperater(AssortedData: list[list[tuple[int, int], DataType]]):
    response = []
    for item in AssortedData:
        if (item[1] == DataType.Exon) or (item[1] == DataType.Intron):
            for index, location in enumerate(item[0]):
                result = {
                    "start_point": location[0],
                    "end_point": location[1],
                    "name": item[1].value + str(index + 1),
                }
                response.append(result)
        else:
            for location in item[0]:
                result = {
                    "start_point": location[0],
                    "end_point": location[1],
                    "name": item[1].value,
                }
                response.append(result)
    return response


def getTransData(request):
    target = request.GET.get("name", None)
    type = request.GET.get("type", None)

    if target is not None:
        WBdata = wormbaseJsonCrawler(target)
        unsplicedData, splicedData = sequenceJsonDataParser(WBdata)
        unsplicedSequence = unsplicedData["sequence"]
        splicedSequence = splicedData["sequence"]

        unsplicedAssortedData = answerParser(unsplicedData)
        
        splicedAssortedData = answerParser(splicedData)
        CDS_Seq = Split_Upper(splicedSequence)[0]
        splicedAssortedData.append(getCDSInfo(splicedSequence))

        if type == "Coding_transcript":
            proteinSeq = getProteinInfo(CDS_Seq)
        else:
            proteinSeq = ""

        response = {
            "unsplicedData": responseOperater(unsplicedAssortedData),
            "unsplicedSeq": unsplicedSequence,
            "splicedData": responseOperater(splicedAssortedData),
            "splicedSeq": splicedSequence,
            "proteinSeq": proteinSeq,
        }
    return JsonResponse(response, safe=False)
