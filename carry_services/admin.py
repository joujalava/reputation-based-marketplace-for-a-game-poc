from django.contrib import admin

from .models import CarryService, CarryServicePotentialBuyer

class CarryServicePotentialBuyerInline(admin.StackedInline):
    model = CarryServicePotentialBuyer
    extra = 0

class CarryServiceAdmin(admin.ModelAdmin):
    list_display = ('price', 'currency', 'seller', 'buyer', 'created_at')
    inlines = [CarryServicePotentialBuyerInline]
    search_fields = ['seller', 'buyer']

admin.site.register(CarryService, CarryServiceAdmin)