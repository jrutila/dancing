from django.contrib import admin
from cms.extensions import PageExtensionAdmin

from .page_extension import TitleImageExtension


class TitleImageExtensionAdmin(PageExtensionAdmin):
    pass

admin.site.register(TitleImageExtension, TitleImageExtensionAdmin)