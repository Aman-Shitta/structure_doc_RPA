from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.urls import reverse
from django.contrib import messages	
from django.contrib.auth.decorators import login_required
from .forms import DocumentForm
from .models import Document
import os
from django.utils import timezone
from django.views import generic
from django.http import JsonResponse
from .extract import extract_attribute
from .config import DOC_KEYS
from .models import Document
# Create your views here.

# def index(request):
# 	return render(request, 'ocr/index.html')

class IndexView(generic.ListView):
    """
    generic List view to show docs list of the month
    """
    model = Document
    template_name = '/home/aman/sebi_chall/structure_doc_RPA/app/ocr/templates/ocr/index.html'
    def get_context_data(self, *args, **kwargs):
        docs = Document.objects.all()
        context = {'docs': docs}
        return context

def upload(request):
    """
    View for handling file uplods
    """
    doc_form  = DocumentForm()
    if request.method == "POST":
        doc_form = DocumentForm(request.POST,request.FILES)
        if doc_form.is_valid():
            doc_obj = doc_form.save(commit=False)

        doc_type = doc_obj.document_type
        doc_obj.save()
        doc_path = doc_obj.document.path
        doc_data = start_extraction(doc_path, doc_type)
        
        Document.objects.filter(id=doc_obj.id).update(doc_data=doc_data)
        
    # extractor = Extractor()
    context = {'form':doc_form}
    return render(request, '/home/aman/sebi_chall/structure_doc_RPA/app/ocr/templates/ocr/upload.html', context)

def start_extraction(doc_path, doc_type):
    out = {}
    document_key_dict = DOC_KEYS[doc_type]
    for item in document_key_dict:
        for label in item['labels']:            
            res = extract_attribute(label, doc_path, item['regex'])
            out.update({item['attribute_name']:res})
    return out

def report(request, id):
    """
    function to generate report of documents
    and sort by name, date, year, month
    """
    doc = Document.objects.filter(id=id).first()
    # breakpoint()
    data = doc.doc_data
    return JsonResponse(data)
