"""Django management command to collect option chain data."""

import asyncio
from django.core.management.base import BaseCommand
from apps.data_collection.models import CollectionJob
from django.utils import timezone
from services.tasks import collect_option_chain_task
from services.ib_data_collector import get_collector


class Command(BaseCommand):
    """Collect option chain data for specified symbols."""

    help = "Collect option chain data from IB Gateway"

    def add_arguments(self, parser):
        parser.add_argument(
            "symbols",
            nargs="+",
            type=str,
            help="Stock symbols to collect options for",
        )
        parser.add_argument(
            "--async",
            action="store_true",
            dest="use_async",
            help="Run collection asynchronously via Celery",
        )
        parser.add_argument(
            "--exchange",
            type=str,
            default=None,
            help="Optional exchange specification (e.g., NASDAQ, NYSE)",
        )

    def handle(self, *args, **options):
        """Handle the command execution."""
        symbols = options["symbols"]
        use_async = options.get("use_async", False)
        exchange = options.get("exchange")

        self.stdout.write(f"Collecting option chains for: {', '.join(symbols)}")

        for symbol in symbols:
            # Create job record using Django ORM
            job = CollectionJob.objects.create(
                job_type="option_chain",
                symbol=symbol,
                exchange=exchange,
                status="running",
                started_at=timezone.now(),
            )

            try:
                if use_async:
                    # Queue Celery task
                    task_result = collect_option_chain_task.delay(symbol)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Queued Celery task {task_result.id} for {symbol}"
                        )
                    )
                else:
                    # Run synchronously using shared business logic
                    # Note: This uses services/ib_data_collector which handles
                    # database operations via SQLAlchemy. The job tracking is
                    # done via Django ORM above.
                    async def run_collection():
                        collector = get_collector()
                        return await collector.collect_option_chain_on_demand(
                            symbol=symbol,
                            exchange=exchange,
                            job_id=job.id,  # Use existing Django job
                            store_contracts=True,
                        )

                    result = asyncio.run(run_collection())

                    # Update job status using Django ORM
                    job.refresh_from_db()  # Refresh from database
                    if result.get("status") == "completed":
                        job.status = "completed"
                        job.records_collected = result.get("records_collected", 0)
                    else:
                        job.status = "failed"
                        job.error_message = result.get("error", "Unknown error")
                    job.completed_at = timezone.now()
                    job.save()

                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Collected {result.get("records_collected", 0)} records for {symbol}'
                        )
                    )
            except Exception as e:
                job.status = "failed"
                job.error_message = str(e)
                job.completed_at = timezone.now()
                job.save()
                self.stdout.write(
                    self.style.ERROR(f"Failed to collect options for {symbol}: {e}")
                )
