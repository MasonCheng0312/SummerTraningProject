from django.shortcuts import render
from django.http import JsonResponse
from . import models
from enum import IntEnum, Enum


class TargetType(IntEnum):
    WBgene = 1
    TranscriptID = 2
    TranscriptName = 3
    GeneName = 4
    OtherName = 5
    DontKnow = 6


class ErrorMessage(Enum):
    Normal = "No Error"
    CantFindTarget = "Can't find target, please try again."


class record:
    def __init__(self, WBgene) -> None:
        self._record_someName = models.DatasourceWithoutgenename.objects.get(
            wbgene_name=WBgene
        )
        self._record_geneNameInfo = models.Genenametowbname.objects.filter(wbgene_name__contains=WBgene)
        self._record_typeInfo = models.WbidToCodingtype.objects.filter(wbgene_name__contains=WBgene)

        self.WBgeneName = WBgene

        self.geneName = [item.genename for item in self._record_geneNameInfo]

        self.transcriptName = self._record_someName.transcriptid
        self.otherName = self._record_someName.othername

        self.length = len(self._record_typeInfo)

        self.transID = [item.transcriptid for item in self._record_typeInfo]
        self.transType = [item.codingtype for item in self._record_typeInfo]


def assort_input(target: str) -> TargetType:
    def is_WBgene(target: str) -> bool:
        return "WB" in target

    def is_GeneName(target: str) -> bool:
        return "-" in target

    if is_WBgene(target):
        return TargetType.WBgene
    elif is_GeneName(target):
        return TargetType.GeneName
    else:
        return TargetType.DontKnow


def get_response(target: str, type: TargetType):
    def get_WBgene_from_geneName(gene_name):
        record = models.Genenametowbname.objects.get(genename=gene_name)
        return record.wbgene_name

    def search(WBgene):
        Data = record(WBgene)
        return_data = {
            "gene_id": Data.WBgeneName,
            "gene_name": Data.geneName,
            "field_oftranscripts": Data.length,
            "transcript_id": Data.transcriptName,
            "other_name": Data.otherName,
        }
        return return_data, Data.transID , Data.transType

    def handle_DontKnow(target, type):
        try:
            WBgene = models.DatasourceWithoutgenename.objects.get(
                othername=target
            ).wbgene_name
            type = TargetType.OtherName
            return WBgene, type
        except:
            pass

        try:
            WBgene = models.DatasourceWithoutgenename.objects.get(
                transcriptid=target
            ).wbgene_name
            type = TargetType.TranscriptName
            return WBgene, type
        except:
            pass

        try:
            WBgene = models.WbidToCodingtype.objects.get(
                transcriptid = target
            ).wbgene_name
            type = TargetType.TranscriptID
            return WBgene, type

        except:
            return "", type

    if type is TargetType.WBgene:
        response , transID, transType= search(target)
        return response, transID, transType, type

    
    elif type is TargetType.GeneName:
        WBgene = get_WBgene_from_geneName(target)
        response , transID , transType= search(WBgene)
        return response, transID, transType, type

    elif type is TargetType.DontKnow:
        WBgene, type = handle_DontKnow(target, type)
        if WBgene:
            response , transID, transType= search(WBgene)
            return response, transID, transType, type
        else:
            return "", "", "", type


def ajax_data(request):
    target = request.POST["target"]
    errorCheck = ErrorMessage.Normal
    type = assort_input(target)
    response, transID, transType,  type = get_response(target, type)
    transData = []
    for index,item in enumerate(transID):
        dict = {
            "transcriptID":item,
            "type":transType[index]    
                }
        transData.append(dict)
    if response == "":
        errorCheck = ErrorMessage.CantFindTarget

    return_result = {
        "response": response,
        "transData": transData,
        "error": errorCheck.value,
        "type": type.name
    }
    return JsonResponse(return_result, safe=False)
    # safe設置為false是因為jsonResponse預設只能傳入dict


def form(request):
    return render(request, "index.html", locals())

def result(request):
    return render(request, "result.html", locals())

def site(request):
    return render(request, "site.html", locals())