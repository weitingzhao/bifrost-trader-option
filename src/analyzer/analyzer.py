"""Profit analyzer for evaluating strategies across different strikes/expirations."""

import logging
from typing import List, Optional
from datetime import datetime

from app_fastapi.database.schemas import (
    OptionsChain,
    StrategyResult,
    StrategyType,
    CoveredCallParams,
    IronCondorParams,
    OptionContract,
    OptionType,
)
from ..strategies import CoveredCall, IronCondor
from ..core.connector.ib import get_connector

logger = logging.getLogger(__name__)


class StrategyAnalyzer:
    """Analyzes option strategies across different strikes and expirations."""

    def __init__(self):
        """Initialize the strategy analyzer."""
        pass

    async def analyze_covered_call(
        self, params: CoveredCallParams, chain: OptionsChain
    ) -> List[StrategyResult]:
        """
        Analyze Covered Call strategy across available call options.

        Args:
            params: CoveredCallParams
            chain: OptionsChain with available contracts

        Returns:
            List of StrategyResult for different call strikes/expirations
        """
        results = []

        # Get stock price if not provided
        stock_price = params.stock_price or chain.underlying_price
        if stock_price is None or stock_price == 0:
            logger.error(f"Stock price not available for {params.symbol}")
            return results

        # Filter call options matching expiration
        call_contracts = [
            c
            for c in chain.contracts
            if c.option_type == OptionType.CALL
            and c.expiration == params.call_expiration
        ]

        if not call_contracts:
            logger.warning(
                f"No call contracts found for {params.symbol} expiring {params.call_expiration}"
            )
            return results

        # Analyze each call contract
        for call_contract in call_contracts:
            try:
                strategy = CoveredCall.from_params(
                    params=params, call_contract=call_contract, stock_price=stock_price
                )

                result = strategy.analyze()
                results.append(result)
            except Exception as e:
                logger.error(
                    f"Error analyzing covered call with strike {call_contract.strike}: {e}"
                )
                continue

        return results

    async def analyze_iron_condor(
        self, params: IronCondorParams, chain: OptionsChain
    ) -> List[StrategyResult]:
        """
        Analyze Iron Condor strategy with specified strikes.

        Args:
            params: IronCondorParams
            chain: OptionsChain with available contracts

        Returns:
            List of StrategyResult (typically one, but could be multiple if analyzing variations)
        """
        results = []

        # Find contracts matching the specified strikes and expiration
        contracts = [c for c in chain.contracts if c.expiration == params.expiration]

        if not contracts:
            logger.warning(
                f"No contracts found for {params.symbol} expiring {params.expiration}"
            )
            return results

        # Find specific contracts
        put_sell = next(
            (
                c
                for c in contracts
                if c.option_type == OptionType.PUT
                and c.strike == params.put_sell_strike
            ),
            None,
        )
        put_buy = next(
            (
                c
                for c in contracts
                if c.option_type == OptionType.PUT and c.strike == params.put_buy_strike
            ),
            None,
        )
        call_sell = next(
            (
                c
                for c in contracts
                if c.option_type == OptionType.CALL
                and c.strike == params.call_sell_strike
            ),
            None,
        )
        call_buy = next(
            (
                c
                for c in contracts
                if c.option_type == OptionType.CALL
                and c.strike == params.call_buy_strike
            ),
            None,
        )

        if not all([put_sell, put_buy, call_sell, call_buy]):
            missing = []
            if not put_sell:
                missing.append(f"put_sell ({params.put_sell_strike})")
            if not put_buy:
                missing.append(f"put_buy ({params.put_buy_strike})")
            if not call_sell:
                missing.append(f"call_sell ({params.call_sell_strike})")
            if not call_buy:
                missing.append(f"call_buy ({params.call_buy_strike})")
            logger.warning(f"Missing contracts for Iron Condor: {', '.join(missing)}")
            return results

        try:
            strategy = IronCondor.from_params(
                params=params,
                put_sell_contract=put_sell,
                put_buy_contract=put_buy,
                call_sell_contract=call_sell,
                call_buy_contract=call_buy,
            )

            result = strategy.analyze()
            results.append(result)
        except Exception as e:
            logger.error(f"Error analyzing iron condor: {e}")

        return results

    async def analyze_iron_condor_variations(
        self,
        symbol: str,
        expiration: str,
        chain: OptionsChain,
        quantity: int = 1,
        min_credit: float = 0.0,
    ) -> List[StrategyResult]:
        """
        Analyze Iron Condor strategy across multiple strike combinations.

        This finds profitable Iron Condor setups by testing different strike combinations.

        Args:
            symbol: Stock symbol
            expiration: Expiration date (YYYYMMDD)
            chain: OptionsChain with available contracts
            quantity: Number of spreads
            min_credit: Minimum net credit required

        Returns:
            List of StrategyResult for different strike combinations
        """
        results = []

        # Get contracts for the expiration
        contracts = [c for c in chain.contracts if c.expiration == expiration]

        if not contracts:
            logger.warning(f"No contracts found for {symbol} expiring {expiration}")
            return results

        # Separate puts and calls
        puts = sorted(
            [c for c in contracts if c.option_type == OptionType.PUT],
            key=lambda x: x.strike,
        )
        calls = sorted(
            [c for c in contracts if c.option_type == OptionType.CALL],
            key=lambda x: x.strike,
        )

        if len(puts) < 2 or len(calls) < 2:
            logger.warning(f"Insufficient contracts for Iron Condor analysis")
            return results

        # Find reasonable strike ranges
        # Put spreads: lower strikes
        # Call spreads: higher strikes
        # Iron Condor: put_sell < call_sell

        # Try different combinations
        for i in range(len(puts) - 1):
            for j in range(i + 1, len(puts)):
                put_buy = puts[i]
                put_sell = puts[j]

                for k in range(len(calls) - 1):
                    for l in range(k + 1, len(calls)):
                        call_sell = calls[k]
                        call_buy = calls[l]

                        # Validate: put_sell should be less than call_sell
                        if put_sell.strike >= call_sell.strike:
                            continue

                        try:
                            params = IronCondorParams(
                                symbol=symbol,
                                put_sell_strike=put_sell.strike,
                                put_buy_strike=put_buy.strike,
                                call_sell_strike=call_sell.strike,
                                call_buy_strike=call_buy.strike,
                                expiration=expiration,
                                quantity=quantity,
                            )

                            strategy = IronCondor.from_params(
                                params=params,
                                put_sell_contract=put_sell,
                                put_buy_contract=put_buy,
                                call_sell_contract=call_sell,
                                call_buy_contract=call_buy,
                            )

                            # Check if meets minimum credit requirement
                            entry_cost = strategy.calculate_entry_cost()
                            if (
                                entry_cost > -min_credit
                            ):  # entry_cost is negative for credit
                                continue

                            result = strategy.analyze()
                            results.append(result)
                        except Exception as e:
                            logger.debug(f"Error analyzing iron condor variation: {e}")
                            continue

        return results

    async def analyze_strategy(
        self, strategy_type: StrategyType, params: dict, chain: OptionsChain
    ) -> List[StrategyResult]:
        """
        Analyze a strategy based on type and parameters.

        Args:
            strategy_type: Type of strategy
            params: Strategy parameters as dictionary
            chain: OptionsChain with available contracts

        Returns:
            List of StrategyResult
        """
        if strategy_type == StrategyType.COVERED_CALL:
            call_params = CoveredCallParams(**params)
            return await self.analyze_covered_call(call_params, chain)
        elif strategy_type == StrategyType.IRON_CONDOR:
            condor_params = IronCondorParams(**params)
            return await self.analyze_iron_condor(condor_params, chain)
        else:
            logger.error(f"Unknown strategy type: {strategy_type}")
            return []


# Global analyzer instance
_analyzer: Optional[StrategyAnalyzer] = None


async def get_analyzer() -> StrategyAnalyzer:
    """Get or create the global strategy analyzer instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = StrategyAnalyzer()
    return _analyzer
