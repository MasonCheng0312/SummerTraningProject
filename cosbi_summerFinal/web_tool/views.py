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
        pass
    pass


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
    def get_geneName(WBgene):
        record = models.Genenametowbname.objects.get(wbgene_name=WBgene)
        return record.genename

    def get_WBgene_from_geneName(gene_name):
        record = models.Genenametowbname.objects.get(genename=gene_name)
        return record.wbgene_name

    def get_transcriptName(WBgene):
        record = models.DatasourceWithoutgenename.objects.get(wbgene_name=WBgene)
        return record.transcriptid

    def get_otherName(WBgene):
        record = models.DatasourceWithoutgenename.objects.get(wbgene_name=WBgene)
        return record.othername

    def get_transcriptID_List(WBgene):
        record = models.GeneTable.objects.get(gene_id=WBgene)
        return record.transcript_id

    def search(WBgene):
        record = models.GeneTable.objects.get(gene_id=WBgene)
        return_data = {
            "gene_id": WBgene,
            "gene_name": get_geneName(WBgene),
            "field_oftranscripts": record.field_oftranscripts,
            "transcript_id": get_transcriptName(WBgene),
            "other_name": get_otherName(WBgene),
        }
        return return_data

    def handle_DontKnow():
        pass

    if type is TargetType.WBgene:
        response = search(target)
        transID = get_transcriptID_List(target)
        return response, transID
    elif type is TargetType.GeneName:
        WBgene = get_WBgene_from_geneName(target)
        response = search(WBgene)
        transID = get_transcriptID_List(WBgene)
        return response, transID
    elif type is TargetType.DontKnow:
        try:        
            if models.DatasourceWithoutgenename.objects.get(othername=target):
                WBgene = models.DatasourceWithoutgenename.objects.get(
                    othername=target
                ).wbgene_name
                response = search(WBgene)
                transID = get_transcriptID_List(WBgene)
                return response, transID
        except:
            pass

        try:
            if models.DatasourceWithoutgenename.objects.get(transcriptid=target):
                WBgene = models.DatasourceWithoutgenename.objects.get(
                    transcriptid=target
                ).wbgene_name
                response = search(WBgene)
                transID = get_transcriptID_List(WBgene)
                return response, transID

        except:
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
    target = request.POST["gene_id"]
    errorCheck = ErrorMessage.Normal
    type = assort_input(target)
    response, transID = get_response(target, type)

    if response == "":
        errorCheck = ErrorMessage.CantFindTarget

    return_result = {
        "response": response,
        "transID": transID,
        "error": errorCheck.value,
    }
    return JsonResponse(return_result, safe=False)
    # safe設置為false是因為jsonResponse預設只能傳入dict


def form(request):
    return render(request, "index.html", locals())
