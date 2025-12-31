"""Django models for options data."""
from django.db import models
from django.utils import timezone

# JSONField is available directly in django.db.models for Django 3.1+
try:
    from django.db.models import JSONField
except ImportError:
    from django.contrib.postgres.fields import JSONField


class Stock(models.Model):
    """Stock symbol and metadata."""
    symbol = models.CharField(max_length=10, unique=True, db_index=True)
    name = models.CharField(max_length=200, blank=True)
    sector = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'stocks'
        ordering = ['symbol']

    def __str__(self):
        return self.symbol


class OptionSnapshot(models.Model):
    """TimescaleDB hypertable for option chain snapshots."""
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='option_snapshots')
    symbol = models.CharField(max_length=10, db_index=True)
    underlying_price = models.FloatField()
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    
    # Option contract data stored as JSON for flexibility
    # In production, consider normalizing into separate OptionContract table
    contracts_data = JSONField(default=list)
    
    # Metadata
    expiration_dates = JSONField(default=list)  # List of available expiration dates
    strike_range = JSONField(default=dict)  # {expiration: [min_strike, max_strike]}
    
    class Meta:
        db_table = 'option_snapshots'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['symbol', '-timestamp']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.symbol} @ {self.timestamp}"


class OptionContract(models.Model):
    """Individual option contract (normalized from snapshot)."""
    OPTION_TYPE_CHOICES = [
        ('CALL', 'Call'),
        ('PUT', 'Put'),
    ]
    
    snapshot = models.ForeignKey(OptionSnapshot, on_delete=models.CASCADE, related_name='contracts')
    symbol = models.CharField(max_length=10, db_index=True)
    strike = models.FloatField(db_index=True)
    expiration = models.CharField(max_length=8, db_index=True)  # YYYYMMDD format
    option_type = models.CharField(max_length=4, choices=OPTION_TYPE_CHOICES)
    
    # Pricing data
    bid = models.FloatField()
    ask = models.FloatField()
    last = models.FloatField(null=True, blank=True)
    mid_price = models.FloatField(null=True, blank=True)  # (bid + ask) / 2
    
    # Volume and open interest
    volume = models.IntegerField(default=0)
    open_interest = models.IntegerField(default=0)
    
    # Greeks
    implied_volatility = models.FloatField(null=True, blank=True)
    delta = models.FloatField(null=True, blank=True)
    gamma = models.FloatField(null=True, blank=True)
    theta = models.FloatField(null=True, blank=True)
    vega = models.FloatField(null=True, blank=True)
    
    # IB contract ID
    contract_id = models.IntegerField(null=True, blank=True, unique=True)
    
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'option_contracts'
        ordering = ['expiration', 'strike', 'option_type']
        indexes = [
            models.Index(fields=['symbol', 'expiration', 'strike']),
            models.Index(fields=['timestamp']),
        ]
        unique_together = [['symbol', 'strike', 'expiration', 'option_type', 'timestamp']]

    def __str__(self):
        return f"{self.symbol} {self.option_type} {self.strike} {self.expiration}"

