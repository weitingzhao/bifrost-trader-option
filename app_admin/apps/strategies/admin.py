"""Django admin for strategies app."""
from django.contrib import admin
from .models import StrategyHistory, MarketConditions


@admin.register(StrategyHistory)
class StrategyHistoryAdmin(admin.ModelAdmin):
    """Admin interface for StrategyHistory model."""
    list_display = ['symbol', 'strategy_type', 'entry_cost', 'max_profit', 'max_loss', 'risk_reward_ratio', 'timestamp']
    list_filter = ['strategy_type', 'symbol', 'timestamp']
    search_fields = ['symbol']
    readonly_fields = ['timestamp', 'created_at']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Strategy Info', {
            'fields': ('stock', 'symbol', 'strategy_type', 'parameters')
        }),
        ('Analysis Results', {
            'fields': ('entry_cost', 'max_profit', 'max_loss', 'breakeven_points', 'profit_profile')
        }),
        ('Greeks', {
            'fields': ('delta', 'gamma', 'theta', 'vega'),
            'classes': ('collapse',)
        }),
        ('Metrics', {
            'fields': ('probability_of_profit', 'risk_reward_ratio')
        }),
        ('Metadata', {
            'fields': ('timestamp', 'created_at')
        }),
    )


@admin.register(MarketConditions)
class MarketConditionsAdmin(admin.ModelAdmin):
    """Admin interface for MarketConditions model."""
    list_display = ['timestamp', 'sp500_price', 'vix', 'market_trend', 'volatility_regime']
    list_filter = ['market_trend', 'volatility_regime', 'timestamp']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'

