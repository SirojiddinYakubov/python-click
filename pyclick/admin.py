from django.contrib import admin
from pyclick.models import ClickTransaction


@admin.register(ClickTransaction)
class ClickTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'click_trans_id', 'merchant_trans_id', 'amount', 'action', 'status', 'sign_datetime')
    list_display_links = ('id',)
    list_filter = ('status',)
    search_fields = ['status', 'id', 'merchant_trans_id']
