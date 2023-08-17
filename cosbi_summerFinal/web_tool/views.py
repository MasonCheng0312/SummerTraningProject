from django.shortcuts import render
from django.http import JsonResponse
from . import models

def ajax_data(request):
    
    search_target = request.POST['gene_id']
    
    try:
        genes = models.GeneTable.objects.filter(gene_id__contains = search_target)
        response = []
        if genes:
            for gene in genes:
                gene_id = gene.gene_id
                transcript = gene.transcript_id
                numbers = gene.field_oftranscripts
                return_data = {
                    'gene_id': gene_id,
                    'transcript_id' : transcript,
                    'field_oftranscripts' : numbers
                }
                response.append(return_data)
        else:
            transcripts = models.GeneTable.objects.filter(transcript_id__contains = search_target)           
        if transcripts:
            for transcript in transcripts:
                gene_id = transcript.gene_id
                transcript_id = transcript.transcript_id
                numbers = transcript.field_oftranscripts
                return_data = {
                    'gene_id': gene_id,
                    'transcript_id' : transcript_id,
                    'field_oftranscripts' : numbers
                }
                print(return_data)
                response.append(return_data)
    except:
        message = 'Something wrong, please check again.'
    
    
    return JsonResponse(response, safe=False)
    # safe設置為false是因為jsonResponse預設只能傳入dict


def form(request):
    return render(request, 'index.html', locals()) 
