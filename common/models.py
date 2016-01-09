from cms.models import CMSPlugin
from django.db import models

# Create your models here.

class HomeSlide(CMSPlugin):
    slide_title = models.CharField(max_length=50, default="Moi")
    slide_text = models.CharField(max_length=300, default="Moi")

