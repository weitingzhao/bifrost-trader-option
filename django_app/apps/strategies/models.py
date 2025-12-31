"""Django models for strategy history."""
from django.db import models
from django.utils import timezone
from apps.options.models import Stock

# JSONField is available directly in django.db.models for Django 3.1+
try:
    from django.db.models import JSONField
except ImportError:
    from django.contrib.postgres.fields import JSONField


class StrategyHistory(models.Model):
    """Historical strategy analysis results."""
    STRATEGY_TYPE_CHOICES = [
        ('covered_call', 'Covered Call'),
        ('iron_condor', 'Iron Condor'),
    ]
    
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='strategies')
    symbol = models.CharField(max_length=10, db_index=True)
    strategy_type = models.CharField(max_length=50, choices=STRATEGY_TYPE_CHOICES, db_index=True)
    
    # Strategy parameters (stored as JSON for flexibility)
    parameters = JSONField(default=dict)
    
    # Analysis results
    entry_cost = models.FloatField()  # Negative for credit, positive for debit
    max_profit = models.FloatField()
    max_loss = models.FloatField()
    breakeven_points = JSONField(default=list)
    profit_profile = JSONField(default=list)  # List of {underlying_price, profit_loss, roi}
    
    # Greeks (optional)
    delta = models.FloatField(null=True, blank=True)
    gamma = models.FloatField(null=True, blank=True)
    theta = models.FloatField(null=True, blank=True)
    vega = models.FloatField(null=True, blank=True)
    
    # Metrics
    probability_of_profit = models.FloatField(null=True, blank=True)
    risk_reward_ratio = models.FloatField(null=True, blank=True)
    
    # Metadata
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'strategy_history'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['symbol', 'strategy_type', '-timestamp']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.symbol} {self.strategy_type} @ {self.timestamp}"


class MarketConditions(models.Model):
    """Market state snapshots for context."""
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    
    # Market indices
    sp500_price = models.FloatField(null=True, blank=True)
    vix = models.FloatField(null=True, blank=True)  # Volatility index
    
    # Market conditions
    market_trend = models.CharField(max_length=20, blank=True)  # 'bullish', 'bearish', 'neutral'
    volatility_regime = models.CharField(max_length=20, blank=True)  # 'low', 'medium', 'high'
    
    # Additional metadata (renamed to avoid SQLAlchemy reserved word)
    meta_data = JSONField(default=dict)

    class Meta:
        db_table = 'market_conditions'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"Market @ {self.timestamp}"

