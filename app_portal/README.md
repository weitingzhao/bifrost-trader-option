# Bifrost Portal UI

Production trading interface built with Vue.js, referencing the Skote Nodejs v4.2.0 Starterkit.

## Status

⚠️ **In Progress**: This portal UI is being set up for full implementation in Phase 4. The Skote Nodejs v4.2.0 Starterkit has been copied here as a design reference.

## Current Structure (Copied from Skote Starterkit)

The `app_portal/` directory now contains the full source code of the Skote Nodejs v4.2.0 Starterkit. This includes:

```
app_portal/
├── app.js              # Main Express.js server application file
├── config.env          # Environment variables (e.g., PORT, DATABASE_LOCAL)
├── controller/         # Express controllers
├── i18n/               # Internationalization files
├── models/             # Mongoose models
├── package.json        # Node.js dependencies and scripts
├── public/             # Static assets (compiled CSS, JS, images, fonts)
├── routes/             # Express route definitions
├── src/                # Source assets (SCSS, uncompiled JS, images)
├── utils/              # Utility functions
├── views/              # EJS templates for rendering UI
└── webpack.config.js   # Webpack configuration
```

**Note**: The `app_portal/api.js` file (for FastAPI integration) has been preserved at the root level.

## API Client

The `app_portal/api.js` file provides functions to interact with the FastAPI backend:

- `fetchOptionsChain(symbol, useCache)` - Get option chain data
- `analyzeStrategy(strategyParams)` - Analyze a trading strategy
- `getStrategyOpportunities(strategyType, filters)` - Get strategy opportunities
- `getHistoricalData(symbol, hours)` - Get historical option data
- `healthCheck()` - Check API health
- `collectData(request)` - Trigger data collection
- `getCollectionJobStatus(jobId)` - Get data collection job status
- `listCollectionJobs(filters)` - List data collection jobs
- `collectDataBatch(request)` - Trigger batch data collection

## Vue.js Conversion Approach

Since the Skote Starterkit is a Node.js/Express (EJS) theme, the plan is to use it as a **design and structural reference** to build the actual Vue.js portal UI.

1.  **Study EJS Templates**: Review the `.ejs` files in `app_portal/views/` to understand the HTML structure, layout, and component composition.
2.  **Recreate in Vue.js**: Develop equivalent Vue.js components (`.vue` files) in `app_portal/src/components/` and `app_portal/src/pages/` that replicate the design and functionality.
3.  **Adopt SCSS**: Integrate the theme's SCSS files (from `app_portal/src/assets/scss/`) into the Vue.js project to maintain the visual style.
4.  **Utilize Layouts**: Adapt the layout patterns (e.g., vertical sidebar, topbar) into Vue.js layout components.
5.  **Integrate API**: Connect Vue.js components to the FastAPI backend using the preserved `app_portal/api.js` client.

## Planned Vue.js Structure (within `app_portal/src/`)

```
app_portal/src/
├── assets/         # Skote theme assets (CSS, JS, images) - adapted
├── components/
│   ├── layout/      # Vue.js layout components (e.g., Sidebar, Topbar, Footer)
│   ├── partials/    # Vue.js reusable UI components (e.g., PageTitle)
│   └── trading/     # Custom Bifrost trading components (e.g., OptionChainTable, StrategyBuilder)
├── pages/          # Vue.js page components (e.g., Dashboard, StrategyAnalyzer)
├── router/         # Vue Router configuration
├── store/          # Pinia state management
└── main.js         # Vue app entry point
```

## Launching the Portal UI

To launch the copied Starterkit for reference:

```bash
./scripts/portal_ui/launch-portal-ui.sh
```

This script will:
- Install Node.js dependencies if needed.
- Use the `PORT` defined in `app_portal/config.env` (default: 4100).
- Handle port conflicts by offering to switch to port 4200 or kill the conflicting process.
- Gracefully handle MongoDB connection issues.

Access the UI in your browser at `http://localhost:4100` (or the alternative port if chosen).

## Git Exclusion

The entire `app_portal/` directory, except for `app_portal/api.js`, `app_portal/README.md`, and `app_portal/.gitkeep`, is excluded from Git via `app_portal/.gitignore`. This ensures that the purchased Starterkit source code is not committed to the repository.
