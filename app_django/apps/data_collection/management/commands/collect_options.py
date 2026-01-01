"""Django management command to collect option chain data."""
import asyncio
from django.core.management.base import BaseCommand
from apps.data_collection.models import CollectionJob
from django.utils import timezone
from services.tasks import collect_option_chain_task
from services.data_collector import collect_option_chain_async
from src.database.connection import get_AsyncSessionLocal


class Command(BaseCommand):
    """Collect option chain data for specified symbols."""
    help = 'Collect option chain data from IB Gateway'

    def add_arguments(self, parser):
        parser.add_argument(
            'symbols',
            nargs='+',
            type=str,
            help='Stock symbols to collect options for',
        )
        parser.add_argument(
            '--async',
            action='store_true',
            dest='use_async',
            help='Run collection asynchronously via Celery',
        )

    def handle(self, *args, **options):
        """Handle the command execution."""
        symbols = options['symbols']
        use_async = options.get('use_async', False)
        
        self.stdout.write(f"Collecting option chains for: {', '.join(symbols)}")
        
        for symbol in symbols:
            # Create job record
            job = CollectionJob.objects.create(
                job_type='option_chain',
                symbol=symbol,
                status='running',
                started_at=timezone.now()
            )
            
            try:
                if use_async:
                    # Queue Celery task
                    task_result = collect_option_chain_task.delay(symbol)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Queued Celery task {task_result.id} for {symbol}'
                        )
                    )
                else:
                    # Run synchronously
                    async def run_collection():
                        AsyncSessionLocal = get_AsyncSessionLocal()
                        async with AsyncSessionLocal() as db:
                            return await collect_option_chain_async(symbol, db)
                    
                    result = asyncio.run(run_collection())
                    job.status = 'completed'
                    job.records_collected = result.get('records_collected', 0)
                    job.completed_at = timezone.now()
                    job.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Collected {result.get("records_collected", 0)} records for {symbol}'
                        )
                    )
            except Exception as e:
                job.status = 'failed'
                job.error_message = str(e)
                job.completed_at = timezone.now()
                job.save()
                self.stdout.write(
                    self.style.ERROR(f'Failed to collect options for {symbol}: {e}')
                )

