# FastAPI Endpoint Development Guide

## Best Practices for Endpoint Development

### 1. Project Structure

```
src/
├── main.py              # FastAPI app and route definitions
├── models.py            # Pydantic request/response models
├── schemas/             # Organized schema modules (recommended)
│   ├── __init__.py
│   ├── requests.py      # Request models
│   ├── responses.py     # Response models
│   └── common.py        # Shared models
├── api/                 # API route modules (recommended)
│   ├── __init__.py
│   ├── v1/              # API versioning
│   │   ├── __init__.py
│   │   ├── endpoints/
│   │   │   ├── options.py
│   │   │   ├── strategies.py
│   │   │   └── health.py
│   │   └── router.py
│   └── dependencies.py   # Shared dependencies
├── services/            # Business logic
│   ├── options_service.py
│   └── strategy_service.py
└── utils/               # Utility functions
```

### 2. Request/Response Model Organization

#### Current Approach (models.py)
- All models in one file
- Good for small projects
- Can become unwieldy as project grows

#### Recommended Approach (schemas/)
- Separate files for requests and responses
- Version-specific schemas
- Better organization and maintainability

### 3. Versioning Strategy

#### Option A: URL Versioning (Recommended)
```python
# src/api/v1/endpoints/options.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["options"])

@router.get("/stocks/{symbol}/options")
async def get_options_v1(symbol: str):
    # Version 1 implementation
    pass

# src/api/v2/endpoints/options.py
@router.get("/stocks/{symbol}/options")
async def get_options_v2(symbol: str):
    # Version 2 with enhanced features
    pass
```

#### Option B: Header Versioning
```python
@router.get("/stocks/{symbol}/options")
async def get_options(
    symbol: str,
    api_version: str = Header(default="v1", alias="X-API-Version")
):
    if api_version == "v1":
        return get_options_v1(symbol)
    elif api_version == "v2":
        return get_options_v2(symbol)
```

### 4. Request/Response Tracking

#### A. OpenAPI/Swagger Documentation
- **Automatic**: FastAPI generates OpenAPI schema
- **Access**: `http://localhost:8000/docs` (Swagger UI)
- **Schema**: `http://localhost:8000/openapi.json`
- **Export**: Save OpenAPI JSON for version control

#### B. Changelog System
```markdown
# CHANGELOG.md
## [1.2.0] - 2024-01-15
### Changed
- `/api/strategies/analyze`: Added `risk_tolerance` parameter
- Response now includes `max_drawdown` field

### Added
- `/api/stocks/{symbol}/options`: New `expiration_filter` query parameter
```

#### C. Schema Registry
- Track all request/response models
- Document breaking changes
- Maintain backward compatibility notes

### 5. Development Workflow

#### Step 1: Define Schema First
```python
# src/schemas/requests.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class OptionsChainRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol", example="AAPL")
    expiration_date: Optional[date] = Field(None, description="Filter by expiration")
    min_volume: Optional[int] = Field(0, ge=0, description="Minimum volume filter")
    
    class Config:
        schema_extra = {
            "example": {
                "symbol": "AAPL",
                "expiration_date": "2024-12-20",
                "min_volume": 100
            }
        }

# src/schemas/responses.py
class OptionsChainResponse(BaseModel):
    symbol: str
    expiration_date: date
    calls: List[OptionContract]
    puts: List[OptionContract]
    timestamp: datetime
    
    class Config:
        schema_extra = {
            "example": {
                "symbol": "AAPL",
                "expiration_date": "2024-12-20",
                "calls": [...],
                "puts": [...],
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
```

#### Step 2: Implement Endpoint
```python
# src/api/v1/endpoints/options.py
from fastapi import APIRouter, Depends, HTTPException
from src.schemas.requests import OptionsChainRequest
from src.schemas.responses import OptionsChainResponse
from src.services.options_service import OptionsService

router = APIRouter(prefix="/api/v1", tags=["options"])

@router.get(
    "/stocks/{symbol}/options",
    response_model=OptionsChainResponse,
    summary="Get options chain for a stock",
    description="Retrieves options chain data with filtering capabilities",
    response_description="Options chain with calls and puts"
)
async def get_options_chain(
    symbol: str,
    request: OptionsChainRequest = Depends(),
    service: OptionsService = Depends(get_options_service)
):
    """
    Get options chain for a stock symbol.
    
    - **symbol**: Stock ticker symbol (e.g., AAPL)
    - **expiration_date**: Optional filter by expiration date
    - **min_volume**: Optional minimum volume filter
    """
    try:
        result = await service.get_options_chain(request)
        return OptionsChainResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

#### Step 3: Document Changes
```python
# Add to endpoint docstring
@router.get(
    "/stocks/{symbol}/options",
    response_model=OptionsChainResponse,
    summary="Get options chain for a stock",
    description="""
    Retrieves options chain data with filtering capabilities.
    
    **Version History:**
    - v1.0.0 (2024-01-01): Initial release
    - v1.1.0 (2024-01-10): Added expiration_date filter
    - v1.2.0 (2024-01-15): Added min_volume filter, response includes timestamp
    """
)
```

### 6. Tracking Tools

#### A. API Versioning File
```python
# src/api/versions.py
"""
API Version Registry
Tracks all endpoint versions and changes
"""

API_VERSIONS = {
    "v1": {
        "version": "1.0.0",
        "release_date": "2024-01-01",
        "endpoints": {
            "/api/v1/stocks/{symbol}/options": {
                "added": "2024-01-01",
                "last_modified": "2024-01-15",
                "request_model": "OptionsChainRequest",
                "response_model": "OptionsChainResponse",
                "changelog": [
                    {
                        "date": "2024-01-15",
                        "version": "1.2.0",
                        "changes": "Added min_volume parameter"
                    }
                ]
            }
        }
    }
}
```

#### B. Schema Diff Tool
```python
# scripts/track_schema_changes.py
"""
Track schema changes between versions
Compares OpenAPI schemas to detect breaking changes
"""
import json
from deepdiff import DeepDiff

def compare_schemas(old_schema, new_schema):
    """Compare two OpenAPI schemas and detect changes"""
    diff = DeepDiff(old_schema, new_schema, ignore_order=True)
    return diff
```

#### C. Automated Testing
```python
# tests/api/test_options_endpoint.py
def test_options_endpoint_request_validation():
    """Test that request schema validation works"""
    from src.schemas.requests import OptionsChainRequest
    
    # Valid request
    valid = OptionsChainRequest(symbol="AAPL")
    assert valid.symbol == "AAPL"
    
    # Invalid request
    with pytest.raises(ValidationError):
        OptionsChainRequest()  # Missing required field

def test_options_endpoint_response_structure():
    """Test that response matches expected schema"""
    response = client.get("/api/v1/stocks/AAPL/options")
    assert response.status_code == 200
    # Validate response structure
    OptionsChainResponse(**response.json())
```

### 7. Recommended Tools

#### A. OpenAPI Generator
- Generate client SDKs from OpenAPI spec
- Validate API contracts
- Generate documentation

#### B. Pydantic Models
- Automatic validation
- Type hints
- JSON schema generation
- Example values

#### C. API Testing
- Postman collections (version controlled)
- Automated integration tests
- Contract testing (Pact, etc.)

#### D. Documentation
- FastAPI auto-generated docs
- Custom documentation site (MkDocs, Sphinx)
- API changelog in README

### 8. Change Management Process

1. **Design Phase**
   - Define request/response models
   - Document in OpenAPI
   - Review with team

2. **Implementation Phase**
   - Implement endpoint
   - Add tests
   - Update documentation

3. **Versioning Phase**
   - Create new version if breaking changes
   - Maintain backward compatibility
   - Update changelog

4. **Deployment Phase**
   - Export OpenAPI schema
   - Update API documentation
   - Notify consumers of changes

### 9. Example: Complete Endpoint Development

```python
# src/schemas/v1/requests.py
class StrategyAnalysisRequest(BaseModel):
    """Request model for strategy analysis endpoint"""
    symbol: str
    strategy_type: StrategyType
    params: Union[CoveredCallParams, IronCondorParams]
    
    class Config:
        schema_extra = {
            "example": {
                "symbol": "AAPL",
                "strategy_type": "covered_call",
                "params": {
                    "strike_price": 150.0,
                    "expiration_date": "2024-12-20"
                }
            }
        }

# src/schemas/v1/responses.py
class StrategyAnalysisResponse(BaseModel):
    """Response model for strategy analysis endpoint"""
    symbol: str
    strategy_type: StrategyType
    analysis: StrategyAnalysisResult
    calculated_at: datetime
    
    class Config:
        schema_extra = {
            "example": {
                "symbol": "AAPL",
                "strategy_type": "covered_call",
                "analysis": {...},
                "calculated_at": "2024-01-15T10:30:00Z"
            }
        }

# src/api/v1/endpoints/strategies.py
@router.post(
    "/strategies/analyze",
    response_model=StrategyAnalysisResponse,
    status_code=200,
    summary="Analyze options trading strategy",
    description="""
    Analyzes an options trading strategy and returns profit/loss projections.
    
    **Version History:**
    - v1.0.0: Initial release with basic P&L calculation
    - v1.1.0: Added Greeks calculation
    - v1.2.0: Added breakeven points and risk metrics
    """
)
async def analyze_strategy(
    request: StrategyAnalysisRequest,
    service: StrategyService = Depends(get_strategy_service)
):
    """Analyze options trading strategy"""
    result = await service.analyze(request)
    return StrategyAnalysisResponse(
        symbol=request.symbol,
        strategy_type=request.strategy_type,
        analysis=result,
        calculated_at=datetime.now()
    )
```

### 10. Monitoring and Tracking

#### A. Logging
```python
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@router.post("/strategies/analyze")
async def analyze_strategy(request: StrategyAnalysisRequest):
    logger.info(f"Strategy analysis requested: {request.dict()}")
    # Track request structure
    logger.debug(f"Request model: {request.__class__.__name__}")
    # ... implementation
    logger.info(f"Response generated: {response.dict()}")
```

#### B. Metrics
- Track endpoint usage
- Monitor request/response sizes
- Alert on schema validation errors

#### C. Audit Trail
- Log all API changes
- Track who made changes
- Document why changes were made

## Quick Reference

### Best Practices Checklist
- [ ] Use Pydantic models for all requests/responses
- [ ] Version your API (URL or header)
- [ ] Document all endpoints with descriptions
- [ ] Include examples in schemas
- [ ] Maintain changelog
- [ ] Write tests for request/response validation
- [ ] Export OpenAPI schema regularly
- [ ] Review breaking changes before deployment
- [ ] Maintain backward compatibility when possible
- [ ] Use type hints everywhere

### File Organization
- Keep schemas separate from business logic
- Group related endpoints in modules
- Use version folders for API versions
- Maintain clear naming conventions

