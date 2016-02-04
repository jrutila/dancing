from django.db import models

from cms.extensions import PageExtension
from cms.extensions.extension_pool import extension_pool
from filer.fields.image import FilerImageField

class TitleImageExtension(PageExtension):
    title_image = FilerImageField(null=True, blank=True,
                           related_name="title_image")

extension_pool.register(TitleImageExtension)

from cms.toolbar_pool import toolbar_pool
from cms.extensions.toolbar import ExtensionToolbar
from django.utils.translation import ugettext_lazy as _
from .models import IconExtension

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