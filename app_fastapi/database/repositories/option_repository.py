"""Repository for option snapshot and contract operations."""
import logging
from typing import List, Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app_fastapi.database.models import OptionSnapshot, OptionContract, Stock
from app_fastapi.database.schemas import OptionsChain, OptionContract as OptionContractSchema

logger = logging.getLogger(__name__)


class OptionRepository:
    """Repository for option data operations."""
    
    @staticmethod
    async def create_option_snapshot(
        symbol: str,
        chain: OptionsChain,
        exchange: Optional[str],
        db: AsyncSession
    ) -> OptionSnapshot:
        """
        Create an option snapshot from an options chain.
        
        Args:
            symbol: Stock symbol
            chain: OptionsChain object
            exchange: Exchange name (optional)
            db: Database session
            
        Returns:
            Created OptionSnapshot
        """
        # Get or create stock record
        result = await db.execute(
            select(Stock).where(Stock.symbol == symbol)
        )
        stock = result.scalar_one_or_none()
        
        if stock is None:
            stock = Stock(symbol=symbol)
            db.add(stock)
            await db.flush()
        
        # Prepare contracts data
        contracts_data = [contract.dict() for contract in chain.contracts]
        expiration_dates = sorted(list(set(c.expiration for c in chain.contracts)))
        strike_range = {}
        for exp in expiration_dates:
            exp_contracts = [c for c in chain.contracts if c.expiration == exp]
            strikes = [c.strike for c in exp_contracts]
            strike_range[exp] = [min(strikes), max(strikes)] if strikes else []
        
        # Create snapshot
        snapshot = OptionSnapshot(
            stock_id=stock.id,
            symbol=symbol,
            underlying_price=chain.underlying_price,
            timestamp=chain.timestamp,
            exchange=exchange,
            contracts_data=contracts_data,
            expiration_dates=expiration_dates,
            strike_range=strike_range,
        )
        
        db.add(snapshot)
        await db.flush()
        
        logger.info(f"Created option snapshot {snapshot.id} for {symbol} with {len(contracts_data)} contracts")
        return snapshot
    
    @staticmethod
    async def create_option_contracts(
        snapshot_id: int,
        contracts: List[OptionContractSchema],
        db: AsyncSession
    ) -> List[OptionContract]:
        """
        Create normalized option contracts from contract schemas.
        
        Args:
            snapshot_id: ID of the parent snapshot
            contracts: List of OptionContract schemas
            db: Database session
            
        Returns:
            List of created OptionContract objects
        """
        option_contracts = []
        
        for contract_schema in contracts:
            # Calculate mid_price
            mid_price = None
            if contract_schema.bid > 0 and contract_schema.ask > 0:
                mid_price = (contract_schema.bid + contract_schema.ask) / 2
            elif contract_schema.last:
                mid_price = contract_schema.last
            
            option_contract = OptionContract(
                snapshot_id=snapshot_id,
                symbol=contract_schema.symbol,
                strike=contract_schema.strike,
                expiration=contract_schema.expiration,
                option_type=contract_schema.option_type.value,
                bid=contract_schema.bid,
                ask=contract_schema.ask,
                last=contract_schema.last,
                mid_price=mid_price,
                volume=contract_schema.volume,
                open_interest=contract_schema.open_interest,
                implied_volatility=contract_schema.implied_volatility,
                delta=contract_schema.delta,
                gamma=contract_schema.gamma,
                theta=contract_schema.theta,
                vega=contract_schema.vega,
                contract_id=contract_schema.contract_id,
                exchange=contract_schema.exchange,
                timestamp=datetime.now(),
            )
            
            option_contracts.append(option_contract)
        
        db.add_all(option_contracts)
        await db.flush()
        
        logger.info(f"Created {len(option_contracts)} normalized option contracts for snapshot {snapshot_id}")
        return option_contracts
    
    @staticmethod
    async def get_latest_snapshot(
        symbol: str,
        exchange: Optional[str] = None,
        db: AsyncSession = None
    ) -> Optional[OptionSnapshot]:
        """
        Get the latest option snapshot for a symbol.
        
        Args:
            symbol: Stock symbol
            exchange: Optional exchange filter
            db: Database session
            
        Returns:
            Latest OptionSnapshot or None
        """
        query = select(OptionSnapshot).where(OptionSnapshot.symbol == symbol)
        
        if exchange:
            query = query.where(OptionSnapshot.exchange == exchange)
        
        query = query.order_by(OptionSnapshot.timestamp.desc()).limit(1)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_contracts_by_snapshot(
        snapshot_id: int,
        db: AsyncSession
    ) -> List[OptionContract]:
        """
        Get all contracts for a snapshot.
        
        Args:
            snapshot_id: Snapshot ID
            db: Database session
            
        Returns:
            List of OptionContract objects
        """
        result = await db.execute(
            select(OptionContract).where(OptionContract.snapshot_id == snapshot_id)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_contracts_by_exchange(
        exchange: str,
        db: AsyncSession,
        limit: Optional[int] = None
    ) -> List[OptionContract]:
        """
        Get contracts by exchange.
        
        Args:
            exchange: Exchange name
            db: Database session
            limit: Optional limit on results
            
        Returns:
            List of OptionContract objects
        """
        query = select(OptionContract).where(OptionContract.exchange == exchange)
        query = query.order_by(OptionContract.timestamp.desc())
        
        if limit:
            query = query.limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())


