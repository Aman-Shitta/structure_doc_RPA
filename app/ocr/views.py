from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.urls import reverse
from django.contrib import messages	
from django.contrib.auth.decorators import login_required
from .forms import DocumentForm
from .models import Document
from django.utils import timezone
from django.views import generic
from django.http import JsonResponse
from .extract import Extractor
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
        # breakpoint()
        if doc_form.is_valid():
            doc_form.save()
    breakpoint()
    # extractor = Extractor()
    context = {'form':doc_form}
    return render(request, '/home/aman/sebi_chall/structure_doc_RPA/app/ocr/templates/ocr/upload.html', context)


def report(request, id):
    """
    function to generate report of documents
    and sort by name, date, year, month
    """
    data = {"abc":"value"}
    return JsonResponse(data)