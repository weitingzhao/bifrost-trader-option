# Bifrost Frontend

Production trading interface built with **Vue.js 3**, using **Skote Nodejs v4.2.0 Starterkit** as design reference.

## Status

🚧 **In Development**: Building custom trading interface based on Skote Starterkit design patterns.

## Theme Reference

The purchased **Skote Nodejs v4.2.0** theme is located in:
```
themes/skote_nodejs_v4.2.0/
```

**Recommended Starting Point**: `Starterkit/` (as per Skote documentation)

**Note**: This theme folder is excluded from git (see `.gitignore`). It contains purchased commercial software.

**Important**: 
- ⚠️ Skote is a **Node.js/Express.js template** (EJS views), NOT Vue.js
- ✅ Use as **design reference only** - convert EJS patterns to Vue.js
- ✅ Reference Starterkit structure for minimal, clean starting point
- ✅ Launch theme: `./themes/launch_skote.sh starterkit` to view in browser

## Project Structure

Based on Skote Starterkit structure (converted to Vue.js):

```
frontend/
├── src/
│   ├── assets/              # Static assets (reference Starterkit/src/assets/)
│   │   ├── scss/           # Styles (reference Starterkit/src/assets/scss/)
│   │   ├── images/         # Images
│   │   └── fonts/          # Fonts
│   ├── components/          # Vue.js components
│   │   ├── layout/         # Layout components (convert from Starterkit/views/layouts/)
│   │   │   ├── VerticalLayout.vue
│   │   │   ├── HorizontalLayout.vue
│   │   │   └── ...
│   │   ├── partials/       # Reusable partials (convert from Starterkit/views/partials/)
│   │   │   ├── Sidebar.vue
│   │   │   ├── Topbar.vue
│   │   │   ├── Footer.vue
│   │   │   └── ...
│   │   └── trading/        # Custom trading components
│   │       ├── OptionChainTable.vue
│   │       ├── StrategyBuilder.vue
│   │       └── ...
│   ├── pages/              # Page components (convert from Starterkit/views/)
│   │   ├── auth/           # Authentication pages
│   │   ├── dashboard/      # Trading dashboard
│   │   ├── options/        # Options chain viewer
│   │   ├── strategies/     # Strategy builder & analyzer
│   │   └── history/        # Historical data viewer
│   ├── router/             # Vue Router configuration
│   ├── services/            # API client (calls FastAPI)
│   │   └── api.js         # FastAPI integration
│   ├── store/              # Pinia state management
│   ├── utils/              # Utility functions
│   └── App.vue            # Main app component
├── public/                 # Static assets
├── package.json           # Dependencies
└── vite.config.js        # Vite build configuration
```

## Starterkit Reference Structure

Reference `themes/skote_nodejs_v4.2.0/Starterkit/` for:

- **Layouts**: `Starterkit/views/layouts/` → Convert to `frontend/src/components/layout/`
- **Partials**: `Starterkit/views/partials/` → Convert to `frontend/src/components/partials/`
- **Pages**: `Starterkit/views/` → Convert to `frontend/src/pages/`
- **Styles**: `Starterkit/src/assets/scss/` → Reference for `frontend/src/assets/scss/`
- **JavaScript**: `Starterkit/src/assets/js/` → Reference patterns for Vue.js logic

## Features

- **Skote Starterkit-Inspired Design**: Clean, minimal UI based on Starterkit patterns
- **Trading Dashboard**: Real-time option chain overview
- **Strategy Builder**: Interactive strategy configuration
- **Option Chain Viewer**: Real-time option chain data tables
- **Historical Data**: Chart visualization with TradingView
- **Profit/Loss Analysis**: P&L visualization and Greeks display
- **Responsive Design**: Mobile and desktop optimized

## Getting Started

1. **Ensure Theme is Available**:
   ```bash
   # Theme should be at:
   themes/skote_nodejs_v4.2.0/Starterkit/
   ```

2. **Launch Starterkit for Reference**:
   ```bash
   ./themes/launch_skote.sh starterkit
   # Access at: http://localhost:4100
   ```

3. **Install Dependencies**:
   ```bash
   npm install
   ```

4. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API URL
   ```

5. **Development Server**:
   ```bash
   npm run dev
   ```

6. **Build for Production**:
   ```bash
   npm run build
   ```

## Conversion Approach

### EJS to Vue.js Conversion

**Reference Starterkit EJS templates and convert to Vue.js:**

1. **Layouts**:
   - `Starterkit/views/layouts/layout.ejs` → `frontend/src/components/layout/VerticalLayout.vue`
   - Study structure, convert EJS includes to Vue components

2. **Partials**:
   - `Starterkit/views/partials/sidebar.ejs` → `frontend/src/components/partials/Sidebar.vue`
   - `Starterkit/views/partials/topbar.ejs` → `frontend/src/components/partials/Topbar.vue`
   - Convert EJS syntax to Vue.js template syntax

3. **Pages**:
   - `Starterkit/views/index.ejs` → `frontend/src/pages/dashboard/Dashboard.vue`
   - `Starterkit/views/pages-starter.ejs` → Reference for blank page structure
   - Convert EJS to Vue.js components

4. **Styling**:
   - Reference `Starterkit/src/assets/scss/` for color schemes, spacing, typography
   - Adapt SCSS variables and mixins for Vue.js components

## API Client

The API client (`src/services/api.js`) provides functions to interact with the FastAPI backend:

- `fetchOptionsChain(symbol, useCache)` - Get option chain data
- `analyzeStrategy(strategyParams)` - Analyze a trading strategy
- `getStrategyOpportunities(strategyType, filters)` - Get strategy opportunities
- `getHistoricalData(symbol, hours)` - Get historical option data
- `healthCheck()` - Check API health
- `collectOptionChain(request)` - Trigger data collection
- `getCollectionJobStatus(jobId)` - Get collection job status

## Deployment

The frontend will be deployed to Web-Server (10.0.0.75) and served via Nginx reverse proxy.

Build output: `dist/` folder

## Key Differences: Starterkit vs Admin

**Starterkit (Recommended)**:
- ✅ Minimal structure - only Auth, blank, and starter pages
- ✅ Clean starting point for custom development
- ✅ Less code to understand and adapt
- ✅ Perfect for building from scratch

**Admin**:
- Full-featured with all demo pages
- More complex structure
- Better for reference when you need specific components

## Next Steps

1. Study Starterkit structure: `themes/skote_nodejs_v4.2.0/Starterkit/`
2. Launch Starterkit: `./themes/launch_skote.sh starterkit`
3. Convert EJS layouts to Vue.js components
4. Build custom trading components
5. Integrate with FastAPI backend

See `themes/THEME_STRUCTURE.md` for detailed structure analysis.

