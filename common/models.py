from cms.models import CMSPlugin
from cms.models.fields import PageField
from django.db import models
from filer.fields.image import FilerImageField

from cms.extensions import PageExtension
from cms.extensions.extension_pool import extension_pool
from filer.fields.image import FilerImageField
from cms.toolbar_pool import toolbar_pool
from cms.extensions.toolbar import ExtensionToolbar
from django.utils.translation import ugettext_lazy as _
import random

class HomeSlide(CMSPlugin):
    slide_title = models.CharField(max_length=50, default="Moi")
    slide_text = models.CharField(max_length=300, default="Moi")
    slide_image = FilerImageField(related_name="slide_image")
    slide_page_link = PageField()

class Activity(CMSPlugin):
    activity_title = models.CharField(max_length=50,default="Moi")
    activity_subtitle = models.CharField(max_length=50,default="Moi")
    activity_text = models.CharField(max_length=300,default="Moi")
    activity_image = FilerImageField(related_name="activity_image")
    activity_page_link = PageField()

class TitleImageExtension(PageExtension):
    title_image = FilerImageField(null=True, blank=True,
                                  related_name="title_image")

extension_pool.register(TitleImageExtension)

@toolbar_pool.register
class TitleImageExtensionToolbar(ExtensionToolbar):
    # defineds the model for the current toolbar
    model = TitleImageExtension

    def populate(self):
        # setup the extension toolbar with permissions and sanity checks
        current_page_menu = self._setup_extension_toolbar()
        # if it's all ok
        if current_page_menu:
            # retrieves the instance of the current extension (if any) and the toolbar item URL
            page_extension, url = self.get_page_extension_admin()
            if url:
                # adds a toolbar item
                current_page_menu.add_modal_item(_('Title Image'), url=url,
                                                 disabled=not self.toolbar.edit_mode)
def get_random_color():
    r = random.randint(0,126) + 127
    g = random.randint(0,126) + 127
    b = random.randint(0,126) + 127
    
    return "#" + ''.join('%02x'%i for i in  [r,g,b])
                                                 
class NameColor(models.Model):
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=10, default=get_random_color)

from danceclub.models import OwnCompetition
from cms.models.fields import PlaceholderField

class CompetitionPage(models.Model):
    competition = models.ForeignKey(OwnCompetition)
    tickets = PlaceholderField('tickets', related_name="competition_tickets")
    description = PlaceholderField('description', related_name="competition_description")
    enroll_help = PlaceholderField('enroll_help', related_name="competition_enroll_help")
    sponsors = PlaceholderField('sponsors', related_name="competition_sponsors")