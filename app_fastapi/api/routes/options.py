"""Options chain routes."""
from fastapi import APIRouter, HTTPException, Query
import logging

from app_fastapi.database.schemas import OptionsChainResponse
from src.core.data.options_chain import get_fetcher

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/api/stocks/{symbol}/options", response_model=OptionsChainResponse)
async def get_options_chain(
    symbol: str,
    use_cache: bool = Query(True, description="Use cached data if available")
):
    """
    Fetch options chain for a stock symbol.
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL', 'TSLA')
        use_cache: Whether to use cached data
        
    Returns:
        OptionsChainResponse with chain data, expirations, and strikes
    """
    try:
        symbol = symbol.upper()
        fetcher = await get_fetcher()
        
        chain = await fetcher.fetch_chain(symbol, use_cache=use_cache)
        
        if chain is None:
            raise HTTPException(
                status_code=404,
                detail=f"Could not fetch options chain for {symbol}. Make sure IB TWS/Gateway is running and the symbol is valid."
            )
        
        # Extract unique expirations and strikes
        expirations = sorted(set(c.expiration for c in chain.contracts))
        strikes = sorted(set(c.strike for c in chain.contracts))
        
        return OptionsChainResponse(
            chain=chain,
            expirations=expirations,
            strikes=strikes
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching options chain for {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

