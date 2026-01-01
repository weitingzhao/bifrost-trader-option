"""Django models for data collection management."""
from django.db import models
from django.utils import timezone


class CollectionJob(models.Model):
    """Track data collection jobs."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    job_type = models.CharField(max_length=50, db_index=True)  # 'option_chain', 'market_data', etc.
    symbol = models.CharField(max_length=10, null=True, blank=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Job metadata
    records_collected = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)

    class Meta:
        db_table = 'collection_jobs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['job_type', 'status', '-created_at']),
        ]

    def __str__(self):
        return f"{self.job_type} - {self.symbol or 'all'} ({self.status})"

