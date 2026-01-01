# Django ORM vs SQLAlchemy ORM: Side-by-Side Comparison

## Overview

Both **Django ORM** and **SQLAlchemy** are **Object-Relational Mapping (ORM)** frameworks that allow you to interact with databases using Python objects instead of raw SQL queries.

### What is ORM?

**Object-Relational Mapping (ORM)** is a programming technique that:
- Maps database tables to Python classes
- Maps table rows to class instances
- Maps table columns to class attributes
- Provides methods to query and manipulate data using Python code instead of SQL

## Key Differences

| Aspect | Django ORM | SQLAlchemy |
|--------|------------|------------|
| **Type** | Active Record Pattern | Data Mapper Pattern |
| **Inheritance** | `models.Model` | `Base` (declarative) |
| **Field Definition** | `models.CharField()`, `models.IntegerField()` | `Column(String())`, `Column(Integer())` |
| **Relationships** | `ForeignKey()`, `ManyToManyField()` | `ForeignKey()`, `relationship()` |
| **Query Syntax** | `Model.objects.filter()` | `session.query(Model).filter()` |
| **Async Support** | Limited (Django 4.1+) | Full async support |
| **Migration System** | Built-in (`makemigrations`) | Alembic (separate) |
| **Admin Interface** | Built-in Django Admin | None (need to build) |
| **Use Case** | Full-stack web framework | Flexible ORM library |

## Side-by-Side Model Comparison

### Example 1: Stock Model

#### Django ORM (`app_django/apps/options/models.py`)

```python
class Stock(models.Model):
    """Stock symbol and metadata."""
    symbol = models.CharField(max_length=10, unique=True, db_index=True)
    name = models.CharField(max_length=200, blank=True)
    sector = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'stocks'
        ordering = ['symbol']

    def __str__(self):
        return self.symbol
```

#### SQLAlchemy (`src/database/models.py`)

```python
class Stock(Base):
    """Stock symbol and metadata (mirrors Django apps.options.models.Stock)."""
    __tablename__ = 'stocks'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=True)
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    option_snapshots = relationship("OptionSnapshot", back_populates="stock")
    strategies = relationship("StrategyHistory", back_populates="stock")
```

#### Key Differences:

1. **Inheritance**:
   - Django: `models.Model` (automatic `id` field)
   - SQLAlchemy: `Base` (must explicitly define `id`)

2. **Field Types**:
   - Django: `models.CharField(max_length=10)`
   - SQLAlchemy: `Column(String(10))`

3. **Nullability**:
   - Django: `blank=True` (form validation) + `null=True` (database)
   - SQLAlchemy: `nullable=True` (database only)

4. **Defaults**:
   - Django: `auto_now_add=True` (Python-level)
   - SQLAlchemy: `server_default=func.now()` (database-level)

5. **Relationships**:
   - Django: Implicit via `ForeignKey` (reverse access via `related_name`)
   - SQLAlchemy: Explicit `relationship()` with `back_populates`

### Example 2: OptionSnapshot Model

#### Django ORM

```python
class OptionSnapshot(models.Model):
    """TimescaleDB hypertable for option chain snapshots."""
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='option_snapshots')
    symbol = models.CharField(max_length=10, db_index=True)
    underlying_price = models.FloatField()
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    
    contracts_data = JSONField(default=list)
    expiration_dates = JSONField(default=list)
    strike_range = JSONField(default=dict)
    
    class Meta:
        db_table = 'option_snapshots'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['symbol', '-timestamp']),
            models.Index(fields=['timestamp']),
        ]
```

#### SQLAlchemy

```python
class OptionSnapshot(Base):
    """TimescaleDB hypertable for option chain snapshots."""
    __tablename__ = 'option_snapshots'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    symbol = Column(String(10), index=True, nullable=False)
    underlying_price = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=func.now(), index=True, nullable=False)
    
    contracts_data = Column(JSON, default=list)
    expiration_dates = Column(JSON, default=list)
    strike_range = Column(JSON, default=dict)
    
    # Relationships
    stock = relationship("Stock", back_populates="option_snapshots")
    contracts = relationship("OptionContract", back_populates="snapshot")
    
    __table_args__ = (
        Index('idx_option_snapshots_symbol_timestamp', 'symbol', 'timestamp'),
        Index('idx_option_snapshots_timestamp', 'timestamp'),
    )
```

#### Key Differences:

1. **Foreign Keys**:
   - Django: `stock = models.ForeignKey(Stock, ...)` (creates `stock_id` automatically)
   - SQLAlchemy: Must define both `stock_id = Column(Integer, ForeignKey(...))` and `stock = relationship(...)`

2. **Indexes**:
   - Django: In `Meta.indexes` list
   - SQLAlchemy: In `__table_args__` tuple

3. **JSON Fields**:
   - Django: `JSONField()` (Django-specific)
   - SQLAlchemy: `Column(JSON)` (SQLAlchemy JSON type)

### Example 3: OptionContract Model

#### Django ORM

```python
class OptionContract(models.Model):
    OPTION_TYPE_CHOICES = [
        ('CALL', 'Call'),
        ('PUT', 'Put'),
    ]
    
    snapshot = models.ForeignKey(OptionSnapshot, on_delete=models.CASCADE, related_name='contracts')
    symbol = models.CharField(max_length=10, db_index=True)
    strike = models.FloatField(db_index=True)
    expiration = models.CharField(max_length=8, db_index=True)
    option_type = models.CharField(max_length=4, choices=OPTION_TYPE_CHOICES)
    
    bid = models.FloatField()
    ask = models.FloatField()
    last = models.FloatField(null=True, blank=True)
    mid_price = models.FloatField(null=True, blank=True)
    
    volume = models.IntegerField(default=0)
    open_interest = models.IntegerField(default=0)
    
    implied_volatility = models.FloatField(null=True, blank=True)
    delta = models.FloatField(null=True, blank=True)
    gamma = models.FloatField(null=True, blank=True)
    theta = models.FloatField(null=True, blank=True)
    vega = models.FloatField(null=True, blank=True)
    
    contract_id = models.IntegerField(null=True, blank=True, unique=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'option_contracts'
        ordering = ['expiration', 'strike', 'option_type']
        indexes = [
            models.Index(fields=['symbol', 'expiration', 'strike']),
            models.Index(fields=['timestamp']),
        ]
        unique_together = [['symbol', 'strike', 'expiration', 'option_type', 'timestamp']]
```

#### SQLAlchemy

```python
class OptionContract(Base):
    """Individual option contract."""
    __tablename__ = 'option_contracts'
    
    id = Column(Integer, primary_key=True)
    snapshot_id = Column(Integer, ForeignKey('option_snapshots.id'), nullable=False)
    symbol = Column(String(10), index=True, nullable=False)
    strike = Column(Float, index=True, nullable=False)
    expiration = Column(String(8), index=True, nullable=False)
    option_type = Column(String(4), nullable=False)  # 'CALL' or 'PUT'
    
    bid = Column(Float, nullable=False)
    ask = Column(Float, nullable=False)
    last = Column(Float, nullable=True)
    mid_price = Column(Float, nullable=True)
    
    volume = Column(Integer, default=0)
    open_interest = Column(Integer, default=0)
    
    implied_volatility = Column(Float, nullable=True)
    delta = Column(Float, nullable=True)
    gamma = Column(Float, nullable=True)
    theta = Column(Float, nullable=True)
    vega = Column(Float, nullable=True)
    
    contract_id = Column(Integer, unique=True, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=func.now(), index=True, nullable=False)
    
    snapshot = relationship("OptionSnapshot", back_populates="contracts")
    
    __table_args__ = (
        Index('idx_option_contracts_symbol_exp_strike', 'symbol', 'expiration', 'strike'),
        Index('idx_option_contracts_timestamp', 'timestamp'),
        UniqueConstraint('symbol', 'strike', 'expiration', 'option_type', 'timestamp', name='uq_option_contract'),
    )
```

#### Key Differences:

1. **Choices/Constraints**:
   - Django: `choices=OPTION_TYPE_CHOICES` (application-level validation)
   - SQLAlchemy: No built-in choices (use `CheckConstraint` or application-level validation)

2. **Unique Constraints**:
   - Django: `unique_together = [['field1', 'field2']]`
   - SQLAlchemy: `UniqueConstraint('field1', 'field2', name='...')`

3. **Defaults**:
   - Django: `default=0` (Python-level)
   - SQLAlchemy: `default=0` (Python-level) or `server_default='0'` (database-level)

## Query Syntax Comparison

### Creating Records

#### Django ORM
```python
# Create
stock = Stock.objects.create(symbol='AAPL', name='Apple Inc.')

# Or
stock = Stock(symbol='AAPL', name='Apple Inc.')
stock.save()
```

#### SQLAlchemy
```python
# Create (async)
stock = Stock(symbol='AAPL', name='Apple Inc.')
session.add(stock)
await session.commit()

# Or (sync)
stock = Stock(symbol='AAPL', name='Apple Inc.')
session.add(stock)
session.commit()
```

### Querying Records

#### Django ORM
```python
# Get all
stocks = Stock.objects.all()

# Filter
stocks = Stock.objects.filter(sector='Technology')

# Get one
stock = Stock.objects.get(symbol='AAPL')

# Related objects
snapshots = stock.option_snapshots.all()
```

#### SQLAlchemy
```python
# Get all (async)
result = await session.execute(select(Stock))
stocks = result.scalars().all()

# Filter (async)
result = await session.execute(
    select(Stock).where(Stock.sector == 'Technology')
)
stocks = result.scalars().all()

# Get one (async)
result = await session.execute(
    select(Stock).where(Stock.symbol == 'AAPL')
)
stock = result.scalar_one_or_none()

# Related objects
snapshots = stock.option_snapshots  # Direct access via relationship
```

### Updating Records

#### Django ORM
```python
stock = Stock.objects.get(symbol='AAPL')
stock.name = 'Apple Inc.'
stock.save()

# Or bulk update
Stock.objects.filter(sector='Technology').update(name='Updated')
```

#### SQLAlchemy
```python
stock = await session.get(Stock, stock_id)
stock.name = 'Apple Inc.'
await session.commit()

# Or bulk update
await session.execute(
    update(Stock)
    .where(Stock.sector == 'Technology')
    .values(name='Updated')
)
await session.commit()
```

### Deleting Records

#### Django ORM
```python
stock = Stock.objects.get(symbol='AAPL')
stock.delete()

# Or bulk delete
Stock.objects.filter(sector='Technology').delete()
```

#### SQLAlchemy
```python
stock = await session.get(Stock, stock_id)
await session.delete(stock)
await session.commit()

# Or bulk delete
await session.execute(delete(Stock).where(Stock.sector == 'Technology'))
await session.commit()
```

## Architecture Patterns

### Django ORM: Active Record Pattern

- **Model = Table + Row + Query Interface**
- Models contain both data and methods to query/manipulate
- `Model.objects` provides query interface
- Simpler, more opinionated
- Example: `Stock.objects.filter(...)`

### SQLAlchemy: Data Mapper Pattern

- **Separation of concerns**: Models are data, Session handles queries
- Models are just data containers
- Session/Query objects handle database operations
- More flexible, less opinionated
- Example: `session.query(Stock).filter(...)`

## When to Use Each

### Use Django ORM When:
- Building Django web applications
- Need built-in admin interface
- Want automatic migrations
- Prefer simpler, more opinionated approach
- Need form validation integration

### Use SQLAlchemy When:
- Building FastAPI/Flask applications
- Need async/await support
- Want more control over queries
- Need complex database operations
- Working with multiple database backends

## In This Project

### Why Both?

1. **Django** (Port 8001):
   - Admin interface for data management
   - Migration system
   - Management commands
   - Data collection tasks

2. **SQLAlchemy** (Port 8000):
   - FastAPI async support
   - High-performance API queries
   - Real-time data operations
   - Better for trading operations

### Synchronization Strategy

Both ORMs access the **same PostgreSQL database** but use different models:

1. **Single Source of Truth**: `scripts/database/schema.sql`
2. **Django Models**: Mirror canonical schema
3. **SQLAlchemy Models**: Mirror Django models
4. **Workflow**: Schema → Django → Migrations → SQLAlchemy

### Key Synchronization Points

1. **Table Names**: Must match (`db_table` in Django, `__tablename__` in SQLAlchemy)
2. **Field Types**: Must map correctly
3. **Indexes**: Must match
4. **Constraints**: Must match
5. **Relationships**: Must be consistent

## Common Mapping Reference

| Django | SQLAlchemy | Notes |
|--------|------------|-------|
| `models.CharField(max_length=10)` | `Column(String(10))` | String length must match |
| `models.IntegerField()` | `Column(Integer)` | Same |
| `models.FloatField()` | `Column(Float)` | Same |
| `models.DateTimeField()` | `Column(DateTime(timezone=True))` | Timezone handling |
| `models.ForeignKey(Model, ...)` | `Column(Integer, ForeignKey(...))` + `relationship()` | Two parts in SQLAlchemy |
| `models.JSONField()` | `Column(JSON)` | JSON support |
| `null=True, blank=True` | `nullable=True` | Django has two concepts |
| `auto_now_add=True` | `server_default=func.now()` | Default handling |
| `unique=True` | `unique=True` | Same |
| `db_index=True` | `index=True` | Same |
| `unique_together` | `UniqueConstraint(...)` | Composite unique |

## Best Practices for This Project

1. **Always start with canonical schema** (`schema.sql`)
2. **Update Django models first** (generates migrations)
3. **Then update SQLAlchemy models** to match
4. **Verify all three are in sync**
5. **Test with both ORMs** to ensure compatibility

## Summary

Both Django ORM and SQLAlchemy are ORM frameworks, but they:
- Use different patterns (Active Record vs Data Mapper)
- Have different syntax and conventions
- Serve different purposes in this project
- Must be kept in sync via the canonical schema workflow

The key is maintaining consistency across all three representations:
1. Canonical SQL schema
2. Django ORM models
3. SQLAlchemy ORM models

