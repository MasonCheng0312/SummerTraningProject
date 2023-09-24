import os
import re
import pandas as pd
import json
import urllib.request
from enum import Enum
from django.http import JsonResponse

# global const
COMMAND = "python3 piTarPrediction.py inputSeq.fa ce none [0,2,2,3,6]"
INPUT_PATH = "inputSeq.fa"
OUTOUT_PATH = "output/piRNA_targeting_sites.json"


class pirScan:
    def __init__(self, transcripID: str) -> None:
        self.transcripID = transcripID

    def _getSequence(self) -> None:
        def _wormbaseJsonCrawler(transcripID: str) -> dict:
            url = (
                "https://wormbase.org/rest/widget/transcript/"
                + transcripID
                + "/sequences"
            )
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Xll; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
                },
            )
            with urllib.request.urlopen(req) as response:
                transcriptData = response.read().decode("utf-8")
            transcriptData: dict = json.loads(transcriptData)
            return transcriptData

        def _parseSequence(transcriptData: dict) -> str:  # 解析爬回來的資料json檔得到sequence
            strand = transcriptData["fields"][
                "unspliced_sequence_context_with_padding"
            ]["data"]["strand"]
            # 判斷正負股

            if strand == "+":
                sequence = transcriptData["fields"]["spliced_sequence_context"]["data"][
                    "positive_strand"
                ]["sequence"]
                # 將所有相關資料都儲存下來，包含位置以及序列等等
            else:
                sequence = transcriptData["fields"]["spliced_sequence_context"]["data"][
                    "negative_strand"
                ]["sequence"]
            return sequence

        data = _wormbaseJsonCrawler(self.transcripID)
        self.sequence = _parseSequence(data)

    def _getInputSeqTable(self) -> list[dict]:
        def Find_Location(sequence: str, templates: list) -> list[tuple[int, int]]:
            result = []
            for template in templates:
                pattern = re.compile(re.escape(template))
                matchResult = pattern.search(sequence)
                if matchResult:
                    result.append(tuple((matchResult.start() + 1, matchResult.end())))
            return result
        
        def Split_Upper(seq: str) -> list[str]:
            pattern = r"[A-Z]+"
            CDS_seq = re.findall(pattern, seq)
            return CDS_seq
        
        def Split_Lower(seq: str) -> list[str]:
            pattern = r"[a-z]+"
            UTR_seq = re.findall(pattern, seq)
            return UTR_seq

        def _getCDS(location:list[tuple[int, int]]) -> dict:            
            start_pt = location[0][0]
            end_pt = location[0][1]
            CDS_record = {
                "start_point":start_pt,
                "end_point":end_pt,
                "type":"CDS",
                    }
            return CDS_record
        
        def _getUTR(location:tuple[int, int]) -> dict:
            start_pt = location[0]
            end_pt = location[1]
            UTR_record = {
                "start_point":start_pt,
                "end_point":end_pt,
                "type":"UTR",
                    }
            return UTR_record
        
        inputSeqTable = []
        CDS_seq = Split_Upper(self.sequence)
        CDSlocation = Find_Location(self.sequence, CDS_seq)
        inputSeqTable.append(_getCDS(CDSlocation))
        UTR_seq = Split_Lower(self.sequence)
        UTRlocation = Find_Location(self.sequence, UTR_seq)
        for item in UTRlocation:
            inputSeqTable.append(_getUTR(item))
        return inputSeqTable
    
    def createInputFile(self) -> None:
        def _writeFile(transcripID: str, sequence: str) -> None:
            firstLine = ">" + transcripID + "_spliced+UTR\n"
            secondLine = sequence
            with open(INPUT_PATH, "w") as file:
                file.write(firstLine)
                file.write(secondLine)

        self._getSequence()
        _writeFile(self.transcripID, self.sequence)

    def Scan_piRNA(self) -> None:
        os.system(COMMAND)
        # input the file with sequence & target name to piRNA target scaner, it will output 2 result file, csv & json.

    def readResult(self) -> dict:
        with open(OUTOUT_PATH, "r") as file:
            data = json.load(file)
        return data

    def operateResponse(self, resultData: dict) -> dict:
        
        def _getMismatchPostion(positionWithTag: str) -> tuple:
            mismatchPosition = []

            pattern = r"<mark[^>]*>(\d+)</mark>"
            matches = re.findall(pattern, positionWithTag)
            for match in matches:
                mismatchPosition.append(match)

            mismatchPosition = tuple(mismatchPosition)
            # transform to tuple make it read only

            return mismatchPosition

        def _countMismatch(originNum: int, mismatchPosition: tuple) -> int:
            wrong = 0
            for position in mismatchPosition:
                if position == "1" or position == "21":
                    wrong = wrong + 1
            return originNum - wrong
        
        def _parseLocation(location_record:str) -> dict:
            splitResult = location_record.split("-")
            record = {
                "start_point":int(splitResult[0]),
                "end_point":int(splitResult[1]),
                      }
            return record
        
        def _createLocationTable(locationData:list) ->list[dict]:
            locationTable = []
            for record in locationData:
                locationTable.append(_parseLocation(record))
            # sorted will make it easy to dicide how height each piRNA rect should locate.
            return locationTable

        def _dicideHeight(locationTable: list[dict]) -> list[dict]:
            class compareResult(Enum):
                UNKNOWN = 0,
                COMPLETE = 1,
            
            for index, record in enumerate(locationTable):
                heightLevel = 0
                stateCheck = compareResult.UNKNOWN

                while index != 0 or stateCheck is not compareResult.COMPLETE:
                    if index == 0:
                        break

                    index = index - 1
                    if record["start_point"] > locationTable[index]["start_point"] and record["start_point"] < locationTable[index]["end_point"]:
                        heightLevel = heightLevel + 1
                    else:
                        stateCheck = compareResult.COMPLETE

                record["height_level"] = heightLevel

            return locationTable
           
        def _operateScanResult(outputDetail: list) -> tuple[list[dict], list[dict]]:
            piRNA_Data = []
            location_Data = []
            for piRNA in outputDetail:
                record = {}
                record["name"] = piRNA[0]
                record["location"] = piRNA[1]
                mismatchPostion = _getMismatchPostion(piRNA[3])
                record["#mismatch"] = _countMismatch(piRNA[2], mismatchPostion)
                record["mismatchPostion"] = mismatchPostion
                record["mismatchPostion with Tag"] = piRNA[3]
                record["Non_GU pair position"] = eval(piRNA[4])
                record["#Non_GU pair seed region"] = piRNA[5]
                record["#GU pair seed region"] = piRNA[6]
                record["#Non_GU pair Non_seed region"] = piRNA[7]
                record["#GU pair Non_seed region"] = piRNA[8]
                record["seq tag in target region"] = piRNA[9]+"<br/>"+piRNA[10]
                record["other data"] = piRNA[11]
                record["reversed piRNA seq"] = piRNA[12]
                record["score"] = piRNA[14]
                piRNA_Data.append(record)
                location_Data.append(piRNA[1])
            location_Table = _createLocationTable(location_Data)

            for index, item in enumerate(location_Table):
                item["name"] = piRNA_Data[index]["name"]
                item["seq_tag"] = piRNA_Data[index]["seq tag in target region"]
                item["score"] = piRNA_Data[index]["score"]
                item["mismatch"] = piRNA_Data[index]["#mismatch"]

            location_Table = sorted(location_Table, key=lambda x:x["start_point"])
            location_Table = _dicideHeight(location_Table)
            print(location_Table)
            return piRNA_Data, location_Table

        response = {}
        response["name"] = self.transcripID
        response["sequence"] = self.sequence
        response["input Seq table"] = self._getInputSeqTable()
        
        operatedScanResult = _operateScanResult(resultData["newout"])
        response["piRNA"] = operatedScanResult[0]
        response["location_Table"] = operatedScanResult[1]
        return response


def getPredictResult(request):
    target = request.GET.get("name", None)

    operator = pirScan(target)
    operator.createInputFile()
    operator.Scan_piRNA()
    resultData = operator.readResult()
    response = operator.operateResponse(resultData)

    return JsonResponse(response)
