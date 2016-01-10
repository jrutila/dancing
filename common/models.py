from cms.models import CMSPlugin
from cms.models.fields import PageField
from django.db import models
from filer.fields.image import FilerImageField


class HomeSlide(CMSPlugin):
    slide_title = models.CharField(max_length=50, default="Moi")
    slide_text = models.CharField(max_length=300, default="Moi")
    slide_image = FilerImageField(related_name="slide_image")
    slide_page_link = PageField()

