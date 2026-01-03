"""Comprehensive Interactive Brokers data collection service."""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from src.core.connector.ib import get_connector
from src.core.data.options_chain import get_fetcher
from src.core.data.exchange import get_exchange_manager
from src.config import config
from app_fastapi.database.connection import get_AsyncSessionLocal
from app_fastapi.database.repositories import OptionRepository, CollectionJobRepository
from app_fastapi.database.schemas import OptionsChain

logger = logging.getLogger(__name__)


class IBDataCollector:
    """Comprehensive IB data collection service with job tracking and error handling."""

    def __init__(self):
        """Initialize the data collector."""
        self.exchange_manager = get_exchange_manager()
        self.max_retries = (
            config.IB_COLLECTION_MAX_RETRIES
            if hasattr(config, "IB_COLLECTION_MAX_RETRIES")
            else 3
        )
        self.retry_delay = (
            config.IB_COLLECTION_RETRY_DELAY
            if hasattr(config, "IB_COLLECTION_RETRY_DELAY")
            else 1.0
        )
        self.store_contracts = (
            config.IB_COLLECTION_STORE_CONTRACTS
            if hasattr(config, "IB_COLLECTION_STORE_CONTRACTS")
            else True
        )

    async def collect_option_chain_on_demand(
        self,
        symbol: str,
        exchange: Optional[str] = None,
        job_id: Optional[int] = None,
        store_contracts: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Collect option chain data on-demand with job tracking.

        Args:
            symbol: Stock symbol to collect
            exchange: Optional exchange specification (auto-detected if not provided)
            job_id: Optional existing job ID (creates new if not provided)
            store_contracts: Whether to store normalized contracts (defaults to config)

        Returns:
            Dict with status, job_id, records_collected, etc.
        """
        symbol = symbol.upper()
        store_contracts = (
            store_contracts if store_contracts is not None else self.store_contracts
        )

        AsyncSessionLocal = get_AsyncSessionLocal()
        async with AsyncSessionLocal() as db:
            try:
                # Create or get job
                if job_id is None:
                    # Detect exchange if not provided
                    if exchange is None:
                        exchange = await self.exchange_manager.detect_stock_exchange(
                            symbol
                        )

                    job = await CollectionJobRepository.create_job(
                        job_type="option_chain", symbol=symbol, exchange=exchange, db=db
                    )
                    job_id = job.id
                else:
                    job = await CollectionJobRepository.get_job(job_id, db)
                    if not job:
                        return {
                            "status": "error",
                            "error": f"Job {job_id} not found",
                            "job_id": job_id,
                        }
                    exchange = exchange or job.symbol  # Use job's exchange if available

                # Update job status to running
                await CollectionJobRepository.update_job_status(
                    job_id, "running", db=db
                )
                await db.commit()

                # Collect data with retry logic
                result = await self._collect_with_retry(
                    symbol, exchange, job_id, store_contracts, db
                )

                return result

            except Exception as e:
                logger.error(
                    f"Error in collect_option_chain_on_demand for {symbol}: {e}",
                    exc_info=True,
                )
                await CollectionJobRepository.update_job_status(
                    job_id, "failed", error_message=str(e), db=db
                )
                await db.commit()
                return {
                    "status": "error",
                    "error": str(e),
                    "job_id": job_id,
                    "symbol": symbol,
                }

    async def _collect_with_retry(
        self, symbol: str, exchange: str, job_id: int, store_contracts: bool, db
    ) -> Dict[str, Any]:
        """
        Collect data with retry logic.

        Args:
            symbol: Stock symbol
            exchange: Exchange name
            job_id: Job ID
            store_contracts: Whether to store normalized contracts
            db: Database session

        Returns:
            Result dict
        """
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(
                    f"Collecting option chain for {symbol} (attempt {attempt}/{self.max_retries})"
                )

                # Get connector and fetcher
                connector = await get_connector()
                fetcher = await get_fetcher()

                # Fetch full option chain
                chain = await fetcher.fetch_options_chain_full(
                    symbol, exchange, use_cache=False
                )

                if not chain or not chain.contracts:
                    error_msg = f"No option chain data found for {symbol}"
                    logger.warning(error_msg)
                    await CollectionJobRepository.update_job_status(
                        job_id, "failed", error_message=error_msg, db=db
                    )
                    await db.commit()
                    return {
                        "status": "no_data",
                        "job_id": job_id,
                        "symbol": symbol,
                        "records_collected": 0,
                    }

                # Store snapshot
                snapshot = await OptionRepository.create_option_snapshot(
                    symbol, chain, exchange, db
                )

                records_collected = len(chain.contracts)

                # Store normalized contracts if requested
                if store_contracts:
                    contracts = await OptionRepository.create_option_contracts(
                        snapshot.id, chain.contracts, db
                    )
                    records_collected = len(contracts)

                await db.commit()

                # Update job status to completed
                await CollectionJobRepository.update_job_status(
                    job_id, "completed", records_collected=records_collected, db=db
                )
                await db.commit()

                logger.info(
                    f"Successfully collected {records_collected} contracts for {symbol}"
                )

                return {
                    "status": "success",
                    "job_id": job_id,
                    "symbol": symbol,
                    "exchange": exchange,
                    "records_collected": records_collected,
                    "snapshot_id": snapshot.id,
                    "underlying_price": chain.underlying_price,
                    "expiration_count": len(set(c.expiration for c in chain.contracts)),
                }

            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt} failed for {symbol}: {e}")

                if attempt < self.max_retries:
                    # Exponential backoff
                    delay = self.retry_delay * (2 ** (attempt - 1))
                    logger.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    # Final attempt failed
                    error_msg = f"Failed after {self.max_retries} attempts: {str(e)}"
                    await CollectionJobRepository.update_job_status(
                        job_id, "failed", error_message=error_msg, db=db
                    )
                    await db.commit()

        return {
            "status": "error",
            "error": str(last_error),
            "job_id": job_id,
            "symbol": symbol,
        }

    async def collect_option_chain_batch(
        self, symbols: List[str], store_contracts: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Collect option chains for multiple symbols.

        Args:
            symbols: List of stock symbols
            store_contracts: Whether to store normalized contracts

        Returns:
            Dict with results for each symbol
        """
        results = []

        for symbol in symbols:
            try:
                result = await self.collect_option_chain_on_demand(
                    symbol, store_contracts=store_contracts
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Error collecting {symbol}: {e}")
                results.append({"status": "error", "error": str(e), "symbol": symbol})

        return {"status": "completed", "total": len(symbols), "results": results}


# Global collector instance
_collector: Optional[IBDataCollector] = None


async def get_collector() -> IBDataCollector:
    """Get or create the global data collector instance."""
    global _collector
    if _collector is None:
        _collector = IBDataCollector()
    return _collector
