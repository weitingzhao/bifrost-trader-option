"""FastAPI application for options trading strategy analyzer."""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..core.config import config
from .routes import health, options, strategies, history, backtesting

# Configure logging
logging.basicConfig(
    level=logging.INFO if not config.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Bifrost Options Trading Strategy Analyzer",
    description="Analyze option strategies using live data from Interactive Brokers",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(options.router)
app.include_router(strategies.router)
app.include_router(history.router)
app.include_router(backtesting.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Bifrost Options Trading Strategy Analyzer API",
        "version": "0.1.0",
        "endpoints": {
            "health": "/api/health",
            "options_chain": "/api/stocks/{symbol}/options",
            "analyze_strategy": "/api/strategies/analyze",
            "profitable_opportunities": "/api/strategies/{strategy_type}",
            "history": "/api/history/options/{symbol}",
            "backtest": "/api/backtesting/run",
            "compare_strategies": "/api/backtesting/compare"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",  # Keep this for uvicorn command line
        host=config.APP_HOST,
        port=config.APP_PORT,
        reload=config.DEBUG
    )

