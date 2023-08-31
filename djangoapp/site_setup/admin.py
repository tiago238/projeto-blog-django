from django.contrib import admin
from site_setup.models import MenuLink

@admin.register(MenuLink)
class MenuLinkAdmin(admin.ModelAdmin):
    list_display = 'text', 'url_or_path',
