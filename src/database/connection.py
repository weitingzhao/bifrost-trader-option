"""Database connection configuration for SQLAlchemy async."""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator, Optional
import logging

logger = logging.getLogger(__name__)

# Lazy initialization - engine created on first access
_engine: Optional[object] = None
_AsyncSessionLocal: Optional[object] = None

# Base class for SQLAlchemy models
Base = declarative_base()


def _get_engine():
    """Get or create the async engine (lazy initialization)."""
    global _engine
    if _engine is None:
        from ..core.config import config
        _engine = create_async_engine(
            config.DATABASE_URL,
            echo=config.DEBUG,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
        )
    return _engine


def _get_session_factory():
    """Get or create the async session factory (lazy initialization)."""
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        engine = _get_engine()
        _AsyncSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _AsyncSessionLocal


# Module-level accessors for backward compatibility
def get_engine():
    """Get the async engine (lazy initialization)."""
    return _get_engine()


def get_AsyncSessionLocal():
    """Get the async session factory (lazy initialization)."""
    return _get_session_factory()


# For backward compatibility, create properties that call the functions
class _EngineProxy:
    """Proxy for lazy engine access."""
    def __getattr__(self, name):
        return getattr(_get_engine(), name)

class _SessionFactoryProxy:
    """Proxy for lazy session factory access."""
    def __call__(self, *args, **kwargs):
        return _get_session_factory()(*args, **kwargs)
    def __getattr__(self, name):
        return getattr(_get_session_factory(), name)

# Create proxy instances
engine = _EngineProxy()
AsyncSessionLocal = _SessionFactoryProxy()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI to get database session.
    
    Usage:
        @app.get("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            # Use db session
            pass
    """
    session_factory = _get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables (create all tables)."""
    engine = _get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized")


async def close_db():
    """Close database connections."""
    engine = _get_engine()
    await engine.dispose()
    logger.info("Database connections closed")
