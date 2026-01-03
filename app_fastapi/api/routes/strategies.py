"""Strategy analysis routes."""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging

from app_fastapi.database.schemas import (
    AnalysisResponse, StrategyRanking, StrategyType,
    FilterCriteria, CoveredCallParams, IronCondorParams
)
from src.core.data.options_chain import get_fetcher
from src.analyzer.analyzer import get_analyzer
from src.analyzer.filter import get_filter_engine

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/api/strategies/analyze", response_model=AnalysisResponse)
async def analyze_strategy(
    strategy_type: StrategyType,
    params: dict,
    filter_criteria: Optional[FilterCriteria] = None
):
    """
    Analyze an option strategy.
    
    Args:
        strategy_type: Type of strategy (covered_call, iron_condor)
        params: Strategy parameters (varies by strategy type)
        filter_criteria: Optional filter criteria
        
    Returns:
        AnalysisResponse with strategy results
    """
    try:
        # Get symbol from params
        symbol = params.get("symbol", "").upper()
        if not symbol:
            raise HTTPException(
                status_code=400,
                detail="Symbol is required in parameters"
            )
        
        # Fetch options chain
        fetcher = await get_fetcher()
        chain = await fetcher.fetch_chain(symbol, use_cache=True)
        
        if chain is None:
            raise HTTPException(
                status_code=404,
                detail=f"Could not fetch options chain for {symbol}"
            )
        
        # Analyze strategy
        analyzer = await get_analyzer()
        
        if strategy_type == StrategyType.COVERED_CALL:
            call_params = CoveredCallParams(**params)
            results = await analyzer.analyze_covered_call(call_params, chain)
        elif strategy_type == StrategyType.IRON_CONDOR:
            condor_params = IronCondorParams(**params)
            results = await analyzer.analyze_iron_condor(condor_params, chain)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported strategy type: {strategy_type}"
            )
        
        # Apply filters if provided
        filtered_results = results
        if filter_criteria:
            filter_engine = get_filter_engine()
            filtered_results = filter_engine.filter(results, filter_criteria)
        
        return AnalysisResponse(
            results=filtered_results,
            total_analyzed=len(results),
            filtered_count=len(filtered_results)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing strategy: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/api/strategies/{strategy_type}", response_model=List[StrategyRanking])
async def get_profitable_opportunities(
    strategy_type: StrategyType,
    symbol: str = Query(..., description="Stock symbol"),
    expiration: Optional[str] = Query(None, description="Expiration date (YYYYMMDD). Required for iron_condor."),
    min_profit: Optional[float] = Query(None, description="Minimum profit"),
    min_risk_reward: Optional[float] = Query(None, description="Minimum risk/reward ratio"),
    min_probability: Optional[float] = Query(None, description="Minimum probability of profit"),
    max_loss: Optional[float] = Query(None, description="Maximum loss"),
    min_premium_collected: Optional[float] = Query(None, description="Minimum premium collected"),
    limit: int = Query(10, description="Maximum number of results to return")
):
    """
    Find profitable strategy opportunities.
    
    Args:
        strategy_type: Type of strategy
        symbol: Stock symbol
        expiration: Expiration date (required for iron_condor)
        min_profit: Minimum profit filter
        min_risk_reward: Minimum risk/reward ratio filter
        min_probability: Minimum probability of profit filter
        max_loss: Maximum loss filter
        min_premium_collected: Minimum premium collected filter
        limit: Maximum number of results
        
    Returns:
        List of ranked strategy opportunities
    """
    try:
        symbol = symbol.upper()
        
        # Fetch options chain
        fetcher = await get_fetcher()
        chain = await fetcher.fetch_chain(symbol, use_cache=True)
        
        if chain is None:
            raise HTTPException(
                status_code=404,
                detail=f"Could not fetch options chain for {symbol}"
            )
        
        # Build filter criteria
        filter_criteria = FilterCriteria(
            symbol=symbol,
            strategy_type=strategy_type,
            min_profit=min_profit,
            min_risk_reward=min_risk_reward,
            min_probability=min_probability,
            max_loss=max_loss,
            min_premium_collected=min_premium_collected
        )
        
        # Analyze strategies
        analyzer = await get_analyzer()
        results = []
        
        if strategy_type == StrategyType.COVERED_CALL:
            # For covered calls, analyze all available call options
            if expiration:
                # Analyze specific expiration
                call_params = CoveredCallParams(
                    symbol=symbol,
                    call_expiration=expiration,
                    stock_quantity=100,
                    call_strike=0.0  # Will be ignored, we analyze all strikes
                )
                results = await analyzer.analyze_covered_call(call_params, chain)
            else:
                # Analyze all expirations
                expirations = sorted(set(c.expiration for c in chain.contracts))
                for exp in expirations[:4]:  # Limit to first 4 expirations
                    call_params = CoveredCallParams(
                        symbol=symbol,
                        call_expiration=exp,
                        stock_quantity=100,
                        call_strike=0.0
                    )
                    exp_results = await analyzer.analyze_covered_call(call_params, chain)
                    results.extend(exp_results)
        
        elif strategy_type == StrategyType.IRON_CONDOR:
            if not expiration:
                raise HTTPException(
                    status_code=400,
                    detail="Expiration is required for iron_condor strategy"
                )
            
            # Find profitable iron condor variations
            results = await analyzer.analyze_iron_condor_variations(
                symbol=symbol,
                expiration=expiration,
                chain=chain,
                quantity=1,
                min_credit=min_premium_collected or 0.0
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported strategy type: {strategy_type}"
            )
        
        # Filter and rank
        filter_engine = get_filter_engine()
        rankings = filter_engine.filter_and_rank(results, filter_criteria)
        
        # Limit results
        return rankings[:limit]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding profitable opportunities: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

