from django.contrib import admin

from .models import Craft, CraftPotentialBuyer

class CraftPotentialBuyerInline(admin.StackedInline):
    model = CraftPotentialBuyer
    extra = 0

class CraftAdmin(admin.ModelAdmin):
    list_display = ('classification', 'amount', 'price', 'currency', 'seller', 'buyer', 'created_at')
    inlines = [CraftPotentialBuyerInline]
    list_filter = ['classification']
    search_fields = ['seller', 'buyer']

admin.site.register(Craft, CraftAdmin)