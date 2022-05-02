from django import forms
from .models import Document


class DocumentForm(forms.ModelForm):
	"""
	Form for uploading docs and name
	"""
	class Meta:
		model = Document
		fields = ['name','document', 'document_type']