"""Django admin for options app."""
from django.contrib import admin
from .models import Stock, OptionSnapshot, OptionContract


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    """Admin interface for Stock model."""
    list_display = ['symbol', 'name', 'sector', 'created_at', 'updated_at']
    list_filter = ['sector', 'created_at']
    search_fields = ['symbol', 'name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(OptionSnapshot)
class OptionSnapshotAdmin(admin.ModelAdmin):
    """Admin interface for OptionSnapshot model."""
    list_display = ['symbol', 'underlying_price', 'timestamp', 'contract_count']
    list_filter = ['symbol', 'timestamp']
    search_fields = ['symbol']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    def contract_count(self, obj):
        """Display number of contracts in snapshot."""
        if isinstance(obj.contracts_data, list):
            return len(obj.contracts_data)
        return 0
    contract_count.short_description = 'Contracts'


@admin.register(OptionContract)
class OptionContractAdmin(admin.ModelAdmin):
    """Admin interface for OptionContract model."""
    list_display = ['symbol', 'option_type', 'strike', 'expiration', 'bid', 'ask', 'volume', 'timestamp']
    list_filter = ['option_type', 'expiration', 'symbol', 'timestamp']
    search_fields = ['symbol', 'expiration']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'

