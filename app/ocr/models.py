from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.conf import settings
# Create your models here.

class Document(models.Model):

	DOC_TYPES = [
		('adh', "Aadhar"),
		('pan', "Pan Card"),
		# ('kyc', "KYC")
	]
	name = models.CharField(max_length=30)
	document = models.FileField(validators=[FileExtensionValidator(['pdf','png','jpeg','jpg','tiff'])], upload_to='documents')
	created_at = models.DateTimeField(auto_now_add=True)
	document_type = models.CharField(max_length=4, choices=DOC_TYPES)
	doc_data = models.JSONField(blank=True, null=True)
	
	def __self__(self) -> None:
		return f"{self.name}"


