from django.contrib import admin
from cms.extensions import PageExtensionAdmin

from .models import TitleImageExtension


class TitleImageExtensionAdmin(PageExtensionAdmin):
    pass

admin.site.register(TitleImageExtension, TitleImageExtensionAdmin)
