import pandas as pd


def is_live(record: list[str]) -> bool:
    return record[1] == "Live"


def is_GeneName(item: str) -> bool:
    return "-" in item


def get_WBname(record: list[str]) -> str:
    return record[0]


def get_transcriptID(record: list[str]) -> str:
    # transcript ID always located at index[2] (if exist)
    transcriptID_candidate = record[2]
    if is_GeneName(transcriptID_candidate):
        return ""
    return transcriptID_candidate


def get_GeneNames(record: list[str]) -> list[str]:
    GeneNames = []
    for item in record:
        if is_GeneName(item):
            GeneNames.append(item)
    return GeneNames


def get_OtherName(record: list[str]) -> str:
    OtherName_candidate = record[-1]
    if is_GeneName(OtherName_candidate):
        return ""
    return OtherName_candidate


PATH = "/home/cosbi2/py_project/summer_training/c_elegans.PRJNA13758.WS289.geneOtherIDs.txt"
SEPARATOR = "\t"
with open(PATH) as file:
    result = []
    for line in file:
        data = line.rstrip("\n").split(SEPARATOR)
        if is_live(data):
            element: dict = {
                "WBgene_name": get_WBname(data),
                "transcriptID": get_transcriptID(data),
                "GeneNames": get_GeneNames(data),
                "OtherName": get_OtherName(data),
            }
        result.append(element)
