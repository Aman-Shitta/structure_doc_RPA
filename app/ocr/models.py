from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.conf import settings
# Create your models here.

class Document(models.Model):
	name = models.CharField(max_length=30)
	document = models.FileField(validators=[FileExtensionValidator(['pdf','png','jpeg','jpg','tiff'])], upload_to='documents')
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.name

class Output(models.Model):
	json_data = models.JSONField()
	document = models.OneToOneField(Document, on_delete=models.CASCADE)
	def __str__(self):
		return self.document.name+"_ExtractedObj"