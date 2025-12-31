# API Changelog

This document tracks all changes to the FastAPI endpoints, including request/response structure modifications.

## Version History

### [Unreleased]

### [1.0.0] - 2024-01-XX
#### Initial Release
- `/api/health` - Health check endpoint
- `/api/stocks/{symbol}/options` - Get options chain
- `/api/strategies/analyze` - Analyze trading strategies

---

## Endpoint Change Log

### `/api/stocks/{symbol}/options`

**Current Version:** 1.0.0

#### Request Structure
```json
{
  "symbol": "string (path parameter)",
  "expiration_date": "date (optional query)",
  "min_volume": "integer (optional query)"
}
```

#### Response Structure
```json
{
  "symbol": "string",
  "expiration_date": "date",
  "calls": ["OptionContract"],
  "puts": ["OptionContract"],
  "timestamp": "datetime"
}
```

#### Change History
- **2024-01-XX (v1.0.0)**: Initial release

---

### `/api/strategies/analyze`

**Current Version:** 1.0.0

#### Request Structure
```json
{
  "symbol": "string",
  "strategy_type": "covered_call | iron_condor",
  "params": {
    // CoveredCallParams or IronCondorParams
  }
}
```

#### Response Structure
```json
{
  "symbol": "string",
  "strategy_type": "string",
  "analysis": {
    "entry_cost": "float",
    "max_profit": "float",
    "max_loss": "float",
    "breakeven_points": ["float"],
    "greeks": {
      "delta": "float",
      "gamma": "float",
      "theta": "float",
      "vega": "float"
    }
  },
  "calculated_at": "datetime"
}
```

#### Change History
- **2024-01-XX (v1.0.0)**: Initial release

---

## Breaking Changes

None yet.

## Deprecation Notices

None yet.

## Migration Guides

None yet.

---

## How to Use This Changelog

1. **Before making changes**: Review this changelog to understand current structure
2. **When making changes**: 
   - Update the relevant endpoint section
   - Add entry to change history
   - Mark as breaking change if applicable
   - Update version number
3. **After deployment**: 
   - Update "Current Version" for modified endpoints
   - Add migration guide if breaking changes

## Schema Files

- OpenAPI schemas are exported to `api_schemas/` directory
- Use `scripts/track_api_changes.py` to export and compare schemas
- Schema files are timestamped for version tracking

