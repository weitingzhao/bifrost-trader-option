"""Periodic option chain data collection service."""

import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from src.core.connector.ib import get_connector
from src.core.data.options_chain import get_fetcher
from app_api.database.connection import get_db, get_AsyncSessionLocal as get_session_factory
from app_api.database.models import OptionSnapshot, Stock
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def collect_option_chain_async(
    symbol: str, db: Optional[AsyncSession] = None
) -> Dict[str, Any]:
    """
    Collect option chain data for a symbol and store in database.

    Args:
        symbol: Stock symbol to collect options for
        db: Optional database session (creates new if not provided)

    Returns:
        dict: Result with status and metadata
    """
    should_close = False
    if db is None:
        db = AsyncSessionLocal()
        should_close = True

    try:
        # Fetch option chain from IB
        fetcher = await get_fetcher()
        options_chain = await fetcher.fetch_options_chain_full(symbol, use_cache=False)

        if not options_chain or not options_chain.contracts:
            logger.warning(f"No option chain data found for {symbol}")
            return {
                "status": "no_data",
                "symbol": symbol,
                "records_collected": 0,
            }

        # Get or create stock record
        stock_result = await db.execute(select(Stock).where(Stock.symbol == symbol))
        stock = stock_result.scalar_one_or_none()

        if stock is None:
            stock = Stock(symbol=symbol)
            db.add(stock)
            await db.flush()

        # Create option snapshot
        contracts_data = [contract.dict() for contract in options_chain.contracts]
        expiration_dates = sorted(
            list(set(c.expiration for c in options_chain.contracts))
        )
        strike_range = {}
        for exp in expiration_dates:
            exp_contracts = [c for c in options_chain.contracts if c.expiration == exp]
            strikes = [c.strike for c in exp_contracts]
            strike_range[exp] = [min(strikes), max(strikes)] if strikes else []

        snapshot = OptionSnapshot(
            stock_id=stock.id,
            symbol=symbol,
            underlying_price=options_chain.underlying_price,
            timestamp=options_chain.timestamp,
            contracts_data=contracts_data,
            expiration_dates=expiration_dates,
            strike_range=strike_range,
        )

        db.add(snapshot)
        await db.commit()

        logger.info(f"Collected {len(contracts_data)} option contracts for {symbol}")

        result = {
            "status": "success",
            "symbol": symbol,
            "records_collected": len(contracts_data),
            "underlying_price": options_chain.underlying_price,
            "expiration_count": len(expiration_dates),
        }

        if should_close:
            await db.close()

        return result

    except Exception as e:
        logger.error(f"Error collecting option chain for {symbol}: {e}", exc_info=True)
        if db:
            await db.rollback()
        if should_close:
            await db.close()
        raise


def collect_option_chain(symbol: str) -> Dict[str, Any]:
    """
    Synchronous wrapper for collect_option_chain_async.
    Used by Celery tasks.

    Args:
        symbol: Stock symbol to collect options for

    Returns:
        dict: Result with status and metadata
    """
    return asyncio.run(_collect_with_session(symbol))


async def _collect_with_session(symbol: str) -> Dict[str, Any]:
    """Helper to run collection with a new database session."""
    AsyncSessionLocal = get_session_factory()
    async with AsyncSessionLocal() as db:
        try:
            result = await collect_option_chain_async(symbol, db)
            return result
        except Exception as e:
            await db.rollback()
            raise
