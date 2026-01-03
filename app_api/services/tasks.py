"""Celery tasks for background job processing."""

from celery import shared_task
import logging
from typing import List, Optional
from datetime import datetime

from app_api.services.celery_app import celery_app
from app_api.services.data_collector import collect_option_chain

logger = logging.getLogger(__name__)


@shared_task(bind=True, name="collect_option_chain_task")
def collect_option_chain_task(self, symbol: str) -> dict:
    """
    Celery task to collect option chain data for a symbol.

    Args:
        symbol: Stock symbol to collect options for

    Returns:
        dict: Task result with status and metadata
    """
    try:
        logger.info(f"Starting option chain collection for {symbol}")
        result = collect_option_chain(symbol)
        logger.info(
            f"Completed option chain collection for {symbol}: {result.get('records_collected', 0)} records"
        )
        return {
            "status": "success",
            "symbol": symbol,
            "records_collected": result.get("records_collected", 0),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as exc:
        logger.error(
            f"Failed to collect option chain for {symbol}: {exc}", exc_info=True
        )
        # Retry the task
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@shared_task(name="collect_multiple_symbols_task")
def collect_multiple_symbols_task(symbols: List[str]) -> dict:
    """
    Celery task to collect option chain data for multiple symbols.

    Args:
        symbols: List of stock symbols

    Returns:
        dict: Task result with status and metadata
    """
    results = []
    for symbol in symbols:
        try:
            # Chain the individual collection task
            task_result = collect_option_chain_task.delay(symbol)
            results.append(
                {
                    "symbol": symbol,
                    "task_id": task_result.id,
                    "status": "queued",
                }
            )
        except Exception as e:
            logger.error(f"Failed to queue collection for {symbol}: {e}")
            results.append(
                {
                    "symbol": symbol,
                    "status": "failed",
                    "error": str(e),
                }
            )

    return {
        "status": "completed",
        "total_symbols": len(symbols),
        "results": results,
        "timestamp": datetime.utcnow().isoformat(),
    }


@shared_task(name="periodic_option_collection_task")
def periodic_option_collection_task(symbols: Optional[List[str]] = None) -> dict:
    """
    Periodic task to collect option chains for a list of symbols.
    This is typically called by APScheduler or Celery Beat.

    Args:
        symbols: List of symbols to collect. If None, uses default watchlist.

    Returns:
        dict: Task result with status and metadata
    """
    if symbols is None:
        # TODO: Load from configuration or database
        symbols = ["SPY", "QQQ", "AAPL", "MSFT", "TSLA"]

    logger.info(f"Starting periodic option collection for {len(symbols)} symbols")
    return collect_multiple_symbols_task.delay(symbols)
