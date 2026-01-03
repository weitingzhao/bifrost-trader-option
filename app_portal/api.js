/**
 * API client for FastAPI backend.
 * 
 * This is a placeholder for the production React/Vue frontend.
 * In Phase 4, this will be replaced with a full frontend implementation.
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://10.0.0.80:8000';

/**
 * Fetch options chain for a symbol.
 * @param {string} symbol - Stock symbol
 * @param {boolean} useCache - Whether to use cached data
 * @returns {Promise<Object>} Options chain data
 */
export async function fetchOptionsChain(symbol, useCache = true) {
  const response = await fetch(
    `${API_BASE_URL}/api/stocks/${symbol}/options?use_cache=${useCache}`
  );
  if (!response.ok) {
    throw new Error(`Failed to fetch options chain: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Analyze a strategy.
 * @param {Object} strategyParams - Strategy parameters
 * @returns {Promise<Object>} Strategy analysis result
 */
export async function analyzeStrategy(strategyParams) {
  const response = await fetch(`${API_BASE_URL}/api/strategies/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(strategyParams),
  });
  if (!response.ok) {
    throw new Error(`Failed to analyze strategy: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get strategy opportunities.
 * @param {string} strategyType - Type of strategy (e.g., 'covered_call', 'iron_condor')
 * @param {Object} filters - Filter criteria
 * @returns {Promise<Object>} Strategy opportunities
 */
export async function getStrategyOpportunities(strategyType, filters = {}) {
  const queryParams = new URLSearchParams(filters);
  const response = await fetch(
    `${API_BASE_URL}/api/strategies/${strategyType}?${queryParams}`
  );
  if (!response.ok) {
    throw new Error(`Failed to get opportunities: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get historical option data.
 * @param {string} symbol - Stock symbol
 * @param {number} hours - Number of hours of history
 * @returns {Promise<Object>} Historical data
 */
export async function getHistoricalData(symbol, hours = 24) {
  const response = await fetch(
    `${API_BASE_URL}/api/history/options/${symbol}?hours=${hours}`
  );
  if (!response.ok) {
    throw new Error(`Failed to get historical data: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Health check.
 * @returns {Promise<Object>} Health status
 */
export async function healthCheck() {
  const response = await fetch(`${API_BASE_URL}/api/health`);
  if (!response.ok) {
    throw new Error(`Health check failed: ${response.statusText}`);
  }
  return response.json();
}
