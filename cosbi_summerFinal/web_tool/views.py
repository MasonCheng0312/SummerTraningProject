from django.shortcuts import render
from django.http import JsonResponse
from . import models

def ajax_data(request):
    
    gene_id = request.POST['gene_id']
    
    try:
        genes = models.GeneTable.objects.filter(gene_id__contains = gene_id)
        response = []
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
        
    except:
        message = 'Something wrong, please check again.'
    
    
    return JsonResponse(response, safe=False)
    # safe設置為false是因為jsonResponse預設只能傳入dict


def form(request):
    return render(request, 'index.html', locals()) 
