"""Filter engine for ranking profitable strategies."""
import logging
from typing import List, Optional, Callable

from app_api.database.schemas import StrategyResult, FilterCriteria, StrategyRanking, StrategyType

logger = logging.getLogger(__name__)


class FilterEngine:
    """Filters and ranks strategy results based on custom criteria."""
    
    def __init__(self):
        """Initialize the filter engine."""
        pass
    
    def filter(
        self,
        results: List[StrategyResult],
        criteria: FilterCriteria
    ) -> List[StrategyResult]:
        """
        Filter strategy results based on criteria.
        
        Args:
            results: List of strategy results to filter
            criteria: Filter criteria
            
        Returns:
            Filtered list of strategy results
        """
        filtered = results
        
        # Filter by symbol
        if criteria.symbol:
            filtered = [r for r in filtered if r.symbol.upper() == criteria.symbol.upper()]
        
        # Filter by strategy type
        if criteria.strategy_type:
            filtered = [r for r in filtered if r.strategy_type == criteria.strategy_type]
        
        # Filter by minimum profit
        if criteria.min_profit is not None:
            filtered = [r for r in filtered if r.max_profit >= criteria.min_profit]
        
        # Filter by minimum risk/reward ratio
        if criteria.min_risk_reward is not None:
            filtered = [
                r for r in filtered
                if r.risk_reward_ratio is not None and r.risk_reward_ratio >= criteria.min_risk_reward
            ]
        
        # Filter by minimum probability of profit
        if criteria.min_probability is not None:
            filtered = [
                r for r in filtered
                if r.probability_of_profit is not None and r.probability_of_profit >= criteria.min_probability
            ]
        
        # Filter by maximum loss
        if criteria.max_loss is not None:
            filtered = [r for r in filtered if r.max_loss <= criteria.max_loss]
        
        # Filter by minimum premium collected (for credit strategies)
        if criteria.min_premium_collected is not None:
            filtered = [
                r for r in filtered
                if r.entry_cost < 0 and abs(r.entry_cost) >= criteria.min_premium_collected
            ]
        
        # Filter by maximum breakeven range
        if criteria.max_breakeven_range is not None:
            filtered = [
                r for r in filtered
                if self._calculate_breakeven_range(r) <= criteria.max_breakeven_range
            ]
        
        return filtered
    
    def _calculate_breakeven_range(self, result: StrategyResult) -> float:
        """
        Calculate the range between breakeven points.
        
        Args:
            result: Strategy result
            
        Returns:
            Range between breakeven points (0 if only one or none)
        """
        if len(result.breakeven_points) < 2:
            return 0.0
        
        prices = [bp.price for bp in result.breakeven_points]
        return max(prices) - min(prices)
    
    def rank(
        self,
        results: List[StrategyResult],
        scoring_function: Optional[Callable[[StrategyResult], float]] = None
    ) -> List[StrategyRanking]:
        """
        Rank strategy results by a scoring function.
        
        Args:
            results: List of strategy results to rank
            scoring_function: Custom scoring function. If None, uses default scoring.
            
        Returns:
            List of ranked strategy results with scores
        """
        if scoring_function is None:
            scoring_function = self._default_scoring_function
        
        rankings = []
        for result in results:
            try:
                score = scoring_function(result)
                metrics = self._calculate_ranking_metrics(result)
                rankings.append(StrategyRanking(
                    result=result,
                    score=score,
                    ranking_metrics=metrics
                ))
            except Exception as e:
                logger.error(f"Error ranking strategy: {e}")
                continue
        
        # Sort by score (descending)
        rankings.sort(key=lambda x: x.score, reverse=True)
        
        return rankings
    
    def _default_scoring_function(self, result: StrategyResult) -> float:
        """
        Default scoring function for strategies.
        
        Combines multiple factors:
        - Max profit (weighted)
        - Risk/reward ratio (weighted)
        - Probability of profit (weighted)
        - Premium collected (for credit strategies)
        
        Args:
            result: Strategy result
            
        Returns:
            Score (higher is better)
        """
        score = 0.0
        
        # Max profit component (normalized, assuming max $10,000)
        profit_score = min(result.max_profit / 10000.0, 1.0) * 0.3
        score += profit_score
        
        # Risk/reward ratio component
        if result.risk_reward_ratio is not None:
            # Normalize to 0-1 range (assuming max R:R of 10)
            rr_score = min(result.risk_reward_ratio / 10.0, 1.0) * 0.3
            score += rr_score
        
        # Probability of profit component
        if result.probability_of_profit is not None:
            prob_score = result.probability_of_profit * 0.2
            score += prob_score
        
        # Premium collected component (for credit strategies)
        if result.entry_cost < 0:  # Credit strategy
            # Normalize premium (assuming max $5,000 credit)
            premium_score = min(abs(result.entry_cost) / 5000.0, 1.0) * 0.2
            score += premium_score
        
        return score
    
    def _calculate_ranking_metrics(self, result: StrategyResult) -> dict:
        """
        Calculate metrics used for ranking.
        
        Args:
            result: Strategy result
            
        Returns:
            Dictionary of ranking metrics
        """
        metrics = {
            "max_profit": result.max_profit,
            "max_loss": result.max_loss,
            "entry_cost": result.entry_cost,
        }
        
        if result.risk_reward_ratio is not None:
            metrics["risk_reward_ratio"] = result.risk_reward_ratio
        
        if result.probability_of_profit is not None:
            metrics["probability_of_profit"] = result.probability_of_profit
        
        if result.greeks:
            metrics["delta"] = result.greeks.delta
            metrics["theta"] = result.greeks.theta
            metrics["vega"] = result.greeks.vega
        
        breakeven_range = self._calculate_breakeven_range(result)
        metrics["breakeven_range"] = breakeven_range
        
        return metrics
    
    def filter_and_rank(
        self,
        results: List[StrategyResult],
        criteria: FilterCriteria,
        scoring_function: Optional[Callable[[StrategyResult], float]] = None
    ) -> List[StrategyRanking]:
        """
        Filter and rank strategy results.
        
        Args:
            results: List of strategy results
            criteria: Filter criteria
            scoring_function: Custom scoring function (optional)
            
        Returns:
            List of ranked and filtered strategy results
        """
        # First filter
        filtered = self.filter(results, criteria)
        
        # Then rank
        ranked = self.rank(filtered, scoring_function)
        
        return ranked


# Global filter engine instance
_filter_engine: Optional[FilterEngine] = None


def get_filter_engine() -> FilterEngine:
    """Get or create the global filter engine instance."""
    global _filter_engine
    if _filter_engine is None:
        _filter_engine = FilterEngine()
    return _filter_engine


