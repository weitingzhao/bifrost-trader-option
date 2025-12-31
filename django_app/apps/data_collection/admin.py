"""Django admin for data collection app."""
from django.contrib import admin
from .models import CollectionJob


@admin.register(CollectionJob)
class CollectionJobAdmin(admin.ModelAdmin):
    """Admin interface for CollectionJob model."""
    list_display = ['job_type', 'symbol', 'status', 'records_collected', 'started_at', 'completed_at', 'created_at']
    list_filter = ['job_type', 'status', 'created_at']
    search_fields = ['symbol', 'job_type']
    readonly_fields = ['created_at', 'started_at', 'completed_at']
    date_hierarchy = 'created_at'

