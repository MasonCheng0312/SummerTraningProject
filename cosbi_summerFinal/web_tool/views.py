from django.shortcuts import render
from django.http import JsonResponse
from . import models
from enum import IntEnum, Enum


class TargetType(IntEnum):
    WBgene = 1
    TranscriptID = 2
    GeneName = 3
    OtherName = 4
    DontKnow = 5


class ErrorMessage(Enum):
    Normal = "No Error"
    CantFindTarget = "Can't find target, please try again."


class record:
    def __init__(self, WBgene) -> None:
        self._record_someName = models.DatasourceWithoutgenename.objects.get(
            wbgene_name=WBgene
        )
        self._record_geneNameInfo = models.Genenametowbname.objects.get(
            wbgene_name=WBgene
        )
        self._record_transInfo = models.GeneTable.objects.get(gene_id=WBgene)

        self.WBgeneName = WBgene

        self.geneName = self._record_geneNameInfo.genename

        self.transcriptName = self._record_someName.transcriptid
        self.otherName = self._record_someName.othername

        self.length = self._record_transInfo.field_oftranscripts
        self.transDetail = eval(self._record_transInfo.transcript_id)


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
        return return_data, Data.transDetail

    def handle_DontKnow(target):
        try:
            WBgene = models.DatasourceWithoutgenename.objects.get(
                othername=target
            ).wbgene_name
            return WBgene
        except:
            pass

        try:
            WBgene = models.DatasourceWithoutgenename.objects.get(
                transcriptid=target
            ).wbgene_name
            return WBgene
        except:
            return ""

    if type is TargetType.WBgene:
        response , transID= search(target)
        return response, transID
    
    elif type is TargetType.GeneName:
        WBgene = get_WBgene_from_geneName(target)
        response , transID = search(WBgene)
        return response, transID

    elif type is TargetType.DontKnow:
        WBgene = handle_DontKnow(target)
        if WBgene:
            response , transID = search(WBgene)
            return response, transID
        else:
            return "", ""

        # try:
        #     if (
        #         len(models.GeneTable.objects.filter(transcript_id__contains=target))
        #         == 1
        #     ):
        #         WBgene = models.GeneTable.objects.filter(
        #             transcript_id__contains=target
        #         ).gene_id

        # except:
        #     return "", ""


def ajax_data(request):
    target = request.POST["target"]
    errorCheck = ErrorMessage.Normal
    type = assort_input(target)
    response, transID = get_response(target, type)
    transData = []
    for item in transID:
        dict = {"transcriptID":item}
        transData.append(dict)

    if response == "":
        errorCheck = ErrorMessage.CantFindTarget

    return_result = {
        "response": response,
        "transID": transData,
        "error": errorCheck.value,
    }
    return JsonResponse(return_result, safe=False)
    # safe設置為false是因為jsonResponse預設只能傳入dict


def form(request):
    return render(request, "index.html", locals())
