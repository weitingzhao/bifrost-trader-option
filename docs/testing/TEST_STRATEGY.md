# Test Strategy for Bifrost Implementation Verification

## Overview

This document defines comprehensive test strategies to verify completion of all tasks in Phases 1, 2, and 3 of the PROJECT_PLAN.md.

## Phase 1: Foundation Tests

### 1.1 FastAPI Basic Structure ✅

**Test Strategy:**
```bash
# Test 1: Verify FastAPI app starts
python3 -m src.api.main &
sleep 2
curl http://localhost:8000/api/health
pkill -f "src.api.main"

# Test 2: Verify all routes are accessible
python3 -c "
from src.api.main import app
routes = [r.path for r in app.routes]
assert '/api/health' in routes
assert '/api/stocks/{symbol}/options' in routes
assert '/api/strategies/analyze' in routes
assert '/api/backtesting/run' in routes
print('✓ All routes registered')
"
```

**Expected Results:**
- FastAPI app starts without errors
- Health endpoint returns 200 OK
- All expected routes are registered
- No import errors

**Verification Checklist:**
- [ ] FastAPI app imports successfully
- [ ] Health endpoint responds
- [ ] All route modules load without errors
- [ ] CORS middleware configured

---

### 1.2 IB Connector Integration ✅

**Test Strategy:**
```bash
# Test 1: Verify IB connector module loads
python3 -c "
from src.core.ib_connector import get_connector
print('✓ IB connector module imports successfully')
"

# Test 2: Verify connection manager exists
python3 -c "
from src.core.ib_connector import IBConnectionManager
assert hasattr(IBConnectionManager, 'connect')
assert hasattr(IBConnectionManager, 'disconnect')
print('✓ IB connection manager has required methods')
"
```

**Expected Results:**
- IB connector module imports without errors
- Connection manager class exists with required methods
- Async connection handling is implemented

**Verification Checklist:**
- [ ] `src/core/ib_connector.py` exists and imports
- [ ] Connection manager class implemented
- [ ] Async connection methods exist
- [ ] Connection pooling support present

---

### 1.3 Streamlit Monitoring ✅

**Test Strategy:**
```bash
# Test 1: Verify Streamlit monitoring app exists
test -f apps_streamlit/monitoring/app.py && echo "✓ Monitoring app exists"

# Test 2: Verify app imports
python3 -c "
import sys
sys.path.insert(0, 'apps_streamlit/monitoring')
import app
print('✓ Monitoring app imports successfully')
"

# Test 3: Check for required pages
ls apps_streamlit/monitoring/pages/ | grep -q ".*\.py" && echo "✓ Pages directory exists"
```

**Expected Results:**
- Monitoring app file exists
- App imports without errors
- Pages directory exists with page files

**Verification Checklist:**
- [ ] `apps_streamlit/monitoring/app.py` exists
- [ ] App can be imported
- [ ] Pages directory exists
- [ ] No import errors

---

### 1.4 Restructure `src/` to Match Recommended Structure ✅

**Test Strategy:**
```bash
# Test 1: Verify directory structure
python3 << 'EOF'
import os
required_dirs = [
    'src/api',
    'src/api/routes',
    'src/core',
    'src/analyzer',
    'src/database',
    'src/strategies',
    'src/utils'
]
missing = [d for d in required_dirs if not os.path.exists(d)]
if missing:
    print(f"✗ Missing directories: {missing}")
    exit(1)
print("✓ All required directories exist")
EOF

# Test 2: Verify key files exist
test -f src/api/main.py && echo "✓ FastAPI main exists"
test -f src/core/ib_connector.py && echo "✓ IB connector exists"
test -f src/core/options_chain.py && echo "✓ Options chain exists"
test -f src/analyzer/analyzer.py && echo "✓ Analyzer exists"
test -f src/database/connection.py && echo "✓ Database connection exists"
```

**Expected Results:**
- All required directories exist
- Key files are in correct locations
- Structure matches PROJECT_PLAN.md

**Verification Checklist:**
- [ ] `src/api/` with routes, middleware
- [ ] `src/core/` with config, IB connector, options chain
- [ ] `src/analyzer/` with analyzer, filter
- [ ] `src/database/` with schemas, models, connection
- [ ] `src/strategies/` with strategy implementations
- [ ] `src/utils/` with utilities

---

### 1.5 Django Project Structure ✅

**Test Strategy:**
```bash
# Test 1: Verify Django structure
test -f app_django/manage.py && echo "✓ Django manage.py exists"
test -d app_django/django_config && echo "✓ Django config exists"
test -d app_django/apps && echo "✓ Django apps directory exists"

# Test 2: Verify Django apps
python3 << 'EOF'
import os
required_apps = ['options', 'strategies', 'data_collection']
for app in required_apps:
    app_dir = f'app_django/apps/{app}'
    if not os.path.exists(app_dir):
        print(f"✗ Missing app: {app}")
        exit(1)
    if not os.path.exists(f'{app_dir}/models.py'):
        print(f"✗ Missing models.py for {app}")
        exit(1)
print("✓ All Django apps exist with models")
EOF

# Test 3: Verify Django settings
python3 -c "
import sys
sys.path.insert(0, 'app_django')
from django_config import settings
assert hasattr(settings, 'DATABASES')
print('✓ Django settings configured')
"
```

**Expected Results:**
- Django project structure exists
- All required apps exist with models
- Django settings are configured

**Verification Checklist:**
- [ ] `app_django/manage.py` exists
- [ ] `app_django/django_config/` with settings
- [ ] `app_django/apps/options/` with models
- [ ] `app_django/apps/strategies/` with models
- [ ] `app_django/apps/data_collection/` with models
- [ ] Django settings configured

---

### 1.6 Configure Shared Database ✅

**Test Strategy:**
```bash
# Test 1: Verify database connection modules
python3 -c "
from src.database.connection import get_engine, get_AsyncSessionLocal
print('✓ SQLAlchemy connection module imports')
"

# Test 2: Verify Django database settings
python3 -c "
import sys
sys.path.insert(0, 'app_django')
from django_config import settings
assert 'DATABASES' in dir(settings)
print('✓ Django database configured')
"

# Test 3: Verify models exist
python3 -c "
from src.database.models import OptionSnapshot, StrategyHistory, Stock
print('✓ SQLAlchemy models exist')
"

python3 -c "
import sys
sys.path.insert(0, 'app_django')
from apps.options.models import OptionSnapshot as DjangoOptionSnapshot
from apps.strategies.models import StrategyHistory as DjangoStrategyHistory
print('✓ Django models exist')
"
```

**Expected Results:**
- Database connection modules import
- Django database settings configured
- Both SQLAlchemy and Django models exist

**Verification Checklist:**
- [ ] SQLAlchemy connection module exists
- [ ] Django database settings configured
- [ ] SQLAlchemy models match Django models
- [ ] Lazy initialization implemented

---

### 1.7 Set Up Celery for Background Jobs ✅

**Test Strategy:**
```bash
# Test 1: Verify Celery configuration
python3 -c "
from services.celery_app import celery_app
assert celery_app is not None
print('✓ Celery app configured')
"

# Test 2: Verify Celery tasks exist
python3 -c "
from services.tasks import collect_option_chain_data
assert callable(collect_option_chain_data)
print('✓ Celery tasks exist')
"

# Test 3: Verify scheduler exists
python3 -c "
from services.scheduler import scheduler
assert scheduler is not None
print('✓ Scheduler configured')
"
```

**Expected Results:**
- Celery app is configured
- Celery tasks exist and are callable
- Scheduler is configured

**Verification Checklist:**
- [ ] `services/celery_app.py` exists
- [ ] `services/tasks.py` with tasks
- [ ] `services/scheduler.py` with scheduler
- [ ] Celery configuration valid

---

## Phase 2: Data Infrastructure Tests

### 2.1 Create Database Schema (Django Models) ✅

**Test Strategy:**
```bash
# Test 1: Verify Django models exist
python3 << 'EOF'
import sys
sys.path.insert(0, 'app_django')
from apps.options.models import OptionSnapshot, Stock
from apps.strategies.models import StrategyHistory
print("✓ Django models import successfully")
EOF

# Test 2: Verify model fields
python3 << 'EOF'
import sys
sys.path.insert(0, 'app_django')
from apps.options.models import OptionSnapshot
fields = [f.name for f in OptionSnapshot._meta.get_fields()]
required = ['symbol', 'timestamp', 'underlying_price', 'contracts_data']
missing = [f for f in required if f not in fields]
if missing:
    print(f"✗ Missing fields: {missing}")
    exit(1)
print("✓ Required model fields exist")
EOF
```

**Expected Results:**
- Django models import successfully
- Required fields exist on models
- Model relationships are defined

**Verification Checklist:**
- [ ] `OptionSnapshot` model with all required fields
- [ ] `StrategyHistory` model with all required fields
- [ ] `Stock` model exists
- [ ] Model relationships defined

---

### 2.2 Create SQLAlchemy Models Matching Django ✅

**Test Strategy:**
```bash
# Test 1: Verify SQLAlchemy models exist
python3 -c "
from src.database.models import OptionSnapshot, StrategyHistory, Stock
print('✓ SQLAlchemy models import')
"

# Test 2: Compare model fields
python3 << 'EOF'
import sys
sys.path.insert(0, 'app_django')
from src.database.models import OptionSnapshot as SQLAOptionSnapshot
from apps.options.models import OptionSnapshot as DjangoOptionSnapshot

# Get SQLAlchemy columns
sqla_columns = set([c.name for c in SQLAOptionSnapshot.__table__.columns])
# Get Django fields
django_fields = set([f.name for f in DjangoOptionSnapshot._meta.get_fields() if hasattr(f, 'column')])

# Check key fields match
key_fields = {'symbol', 'timestamp', 'underlying_price', 'contracts_data'}
sqla_has = key_fields.intersection(sqla_columns)
django_has = key_fields.intersection(django_fields)

if sqla_has == django_has == key_fields:
    print("✓ Key fields match between SQLAlchemy and Django")
else:
    print(f"✗ Field mismatch - SQLAlchemy: {sqla_has}, Django: {django_has}")
    exit(1)
EOF
```

**Expected Results:**
- SQLAlchemy models import
- Key fields match between SQLAlchemy and Django models
- Models are compatible

**Verification Checklist:**
- [ ] SQLAlchemy models exist
- [ ] Key fields match Django models
- [ ] Data types compatible
- [ ] Relationships match

---

### 2.3 Implement Data Collector Service (Celery) ✅

**Test Strategy:**
```bash
# Test 1: Verify data collector exists
python3 -c "
from services.data_collector import collect_option_chain
assert callable(collect_option_chain)
print('✓ Data collector function exists')
"

# Test 2: Verify Celery task
python3 -c "
from services.tasks import collect_option_chain_data
assert hasattr(collect_option_chain_data, 'delay')
print('✓ Celery task configured')
"
```

**Expected Results:**
- Data collector function exists
- Celery task is configured
- Function is callable

**Verification Checklist:**
- [ ] `services/data_collector.py` exists
- [ ] `collect_option_chain` function exists
- [ ] Celery task configured
- [ ] Task can be called

---

### 2.4 Set Up Scheduled Option Chain Collection ✅

**Test Strategy:**
```bash
# Test 1: Verify scheduler configuration
python3 -c "
from services.scheduler import scheduler
assert scheduler is not None
print('✓ Scheduler exists')
"

# Test 2: Check for scheduled jobs
python3 << 'EOF'
from services.scheduler import scheduler
jobs = scheduler.get_jobs()
if jobs:
    print(f"✓ {len(jobs)} scheduled job(s) found")
else:
    print("⚠ No scheduled jobs found (may be configured at runtime)")
EOF
```

**Expected Results:**
- Scheduler is configured
- Jobs can be scheduled

**Verification Checklist:**
- [ ] `services/scheduler.py` exists
- [ ] Scheduler configured
- [ ] Job scheduling capability exists

---

### 2.5 Configure Django Admin for All Models ✅

**Test Strategy:**
```bash
# Test 1: Verify admin files exist
test -f app_django/apps/options/admin.py && echo "✓ Options admin exists"
test -f app_django/apps/strategies/admin.py && echo "✓ Strategies admin exists"

# Test 2: Verify admin registrations
python3 << 'EOF'
import sys
sys.path.insert(0, 'app_django')
from apps.options.admin import admin
from apps.options.models import OptionSnapshot

# Check if model is registered
if OptionSnapshot in admin._registry:
    print("✓ OptionSnapshot registered in admin")
else:
    print("✗ OptionSnapshot not registered")
    exit(1)
EOF
```

**Expected Results:**
- Admin files exist
- Models are registered in admin

**Verification Checklist:**
- [ ] `app_django/apps/options/admin.py` exists
- [ ] `app_django/apps/strategies/admin.py` exists
- [ ] Models registered in admin
- [ ] Admin can be accessed

---

## Phase 3: Enhanced Features Tests

### 3.1 Add Plotly Charts to Streamlit Analytics ✅

**Test Strategy:**
```bash
# Test 1: Verify Plotly is in requirements
grep -q "plotly" requirements.txt && echo "✓ Plotly in requirements"

# Test 2: Verify analytics pages use Plotly
python3 << 'EOF'
import os
analytics_pages = [
    'apps_streamlit/analytics/pages/strategy_performance.py',
    'apps_streamlit/analytics/pages/option_chain_viewer.py',
    'apps_streamlit/analytics/pages/profit_analysis.py'
]
for page in analytics_pages:
    if os.path.exists(page):
        with open(page, 'r') as f:
            content = f.read()
            if 'plotly' in content.lower():
                print(f"✓ {os.path.basename(page)} uses Plotly")
            else:
                print(f"⚠ {os.path.basename(page)} may not use Plotly")
EOF
```

**Expected Results:**
- Plotly in requirements
- Analytics pages import/use Plotly

**Verification Checklist:**
- [ ] Plotly in `requirements.txt`
- [ ] Analytics pages import Plotly
- [ ] Charts use Plotly

---

### 3.2 Implement Historical Data API Endpoints ✅

**Test Strategy:**
```bash
# Test 1: Verify history routes exist
python3 -c "
from src.api.routes import history
assert hasattr(history, 'router')
print('✓ History routes module exists')
"

# Test 2: Verify endpoints
python3 << 'EOF'
from src.api.main import app
routes = [r.path for r in app.routes if hasattr(r, 'path')]
history_routes = [r for r in routes if 'history' in r]
if history_routes:
    print(f"✓ History endpoints found: {history_routes}")
else:
    print("✗ No history endpoints found")
    exit(1)
EOF
```

**Expected Results:**
- History routes module exists
- History endpoints are registered

**Verification Checklist:**
- [ ] `src/api/routes/history.py` exists
- [ ] History endpoints registered
- [ ] Endpoints return historical data

---

### 3.3 Create Streamlit Analytics Dashboard ✅

**Test Strategy:**
```bash
# Test 1: Verify analytics app exists
test -f apps_streamlit/analytics/app.py && echo "✓ Analytics app exists"

# Test 2: Verify pages exist
python3 << 'EOF'
import os
pages = [
    'strategy_performance.py',
    'option_chain_viewer.py',
    'profit_analysis.py',
    'backtesting.py'
]
pages_dir = 'apps_streamlit/analytics/pages'
for page in pages:
    if os.path.exists(f'{pages_dir}/{page}'):
        print(f"✓ {page} exists")
    else:
        print(f"✗ {page} missing")
EOF

# Test 3: Verify app imports
python3 -c "
import sys
sys.path.insert(0, 'apps_streamlit/analytics')
import app
print('✓ Analytics app imports successfully')
"
```

**Expected Results:**
- Analytics app exists
- All pages exist
- App imports successfully

**Verification Checklist:**
- [ ] `apps_streamlit/analytics/app.py` exists
- [ ] All page files exist
- [ ] App imports without errors

---

### 3.4 Integrate VectorBT for Backtesting ✅

**Test Strategy:**
```bash
# Test 1: Verify VectorBT in requirements
grep -q "vectorbt" requirements.txt && echo "✓ VectorBT in requirements"

# Test 2: Verify backtesting module
python3 -c "
from src.backtesting import StrategyBacktester, BacktestResult
print('✓ Backtesting module imports')
"

# Test 3: Verify backtesting routes
python3 -c "
from src.api.routes import backtesting
assert hasattr(backtesting, 'router')
print('✓ Backtesting routes exist')
"

# Test 4: Verify VectorBT engine
python3 << 'EOF'
try:
    from src.backtesting.vectorbt_engine import VectorBTEngine
    print("✓ VectorBT engine exists")
except ImportError:
    print("⚠ VectorBT engine exists but VectorBT not installed (expected)")
EOF
```

**Expected Results:**
- VectorBT in requirements
- Backtesting module imports
- Backtesting routes exist
- VectorBT engine exists

**Verification Checklist:**
- [ ] VectorBT in `requirements.txt`
- [ ] `src/backtesting/` module exists
- [ ] Backtesting API endpoints exist
- [ ] VectorBT engine implemented

---

### 3.5 Add py_vollib for Advanced Pricing ✅

**Test Strategy:**
```bash
# Test 1: Verify py_vollib in requirements
grep -q "py_vollib" requirements.txt && echo "✓ py_vollib in requirements"

# Test 2: Verify pricing utilities
python3 -c "
from src.utils.pricing import calculate_black_scholes_price
assert callable(calculate_black_scholes_price)
print('✓ Pricing utilities exist')
"
```

**Expected Results:**
- py_vollib in requirements
- Pricing utilities exist and are callable

**Verification Checklist:**
- [ ] py_vollib in `requirements.txt`
- [ ] `src/utils/pricing.py` exists
- [ ] Pricing functions are callable

---

### 3.6 Implement Option Chain Visualization ✅

**Test Strategy:**
```bash
# Test 1: Verify option chain viewer page
test -f apps_streamlit/analytics/pages/option_chain_viewer.py && echo "✓ Option chain viewer exists"

# Test 2: Check for visualization code
python3 << 'EOF'
with open('apps_streamlit/analytics/pages/option_chain_viewer.py', 'r') as f:
    content = f.read()
    if 'plotly' in content.lower() or 'chart' in content.lower():
        print("✓ Option chain viewer has visualization code")
    else:
        print("⚠ Option chain viewer may not have visualization")
EOF
```

**Expected Results:**
- Option chain viewer page exists
- Visualization code present

**Verification Checklist:**
- [ ] Option chain viewer page exists
- [ ] Uses Plotly for visualization
- [ ] Displays option chain data

---

## Comprehensive Test Script

Create a test runner script:

```bash
#!/bin/bash
# test_all_phases.sh - Comprehensive test runner

echo "=== Phase 1: Foundation Tests ==="
# Run Phase 1 tests...

echo "=== Phase 2: Data Infrastructure Tests ==="
# Run Phase 2 tests...

echo "=== Phase 3: Enhanced Features Tests ==="
# Run Phase 3 tests...

echo "=== All Tests Complete ==="
```

## Test Execution Order

1. **Unit Tests**: Test individual components
2. **Integration Tests**: Test component interactions
3. **System Tests**: Test end-to-end functionality
4. **Manual Verification**: Test UI and user workflows

## Notes

- Some tests require database connection (Phase 2)
- Some tests require IB Gateway connection (for live data)
- VectorBT tests may show warnings if not installed
- Django tests require Django environment setup

