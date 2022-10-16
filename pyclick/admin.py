from django.contrib import admin
from pyclick.models import ClickTransaction


@admin.register(ClickTransaction)
class ClickTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'click_paydoc_id', 'amount', 'status',)
    list_display_links = ('id', 'amount')
    list_filter = ('status',)
    search_fields = ['status', 'id', 'click_paydoc_id']
    save_on_top = True
