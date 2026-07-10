from django.contrib import admin
from .models import Listing


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'city', 'price', 'rooms',
                    'property_type', 'is_active', 'owner')
    list_filter = ('property_type', 'is_active', 'city')
    search_fields = ('title', 'description', 'city')
