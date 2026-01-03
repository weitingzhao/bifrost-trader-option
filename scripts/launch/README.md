# Portal UI Development Scripts

This directory contains scripts for managing and developing the Bifrost portal UI.

## Scripts

### `launch-portal.sh`

Launches the Bifrost portal UI (Skote Starterkit-based) for development and testing.

**Usage:**
```bash
./scripts/launch/launch-portal.sh
```

**Features:**
- ✅ Auto-installs dependencies if `node_modules` is missing
- ✅ Uses existing `config.env` or creates default
- ✅ Checks if port is already in use and offers resolution options (switch port, kill process, exit)
- ✅ Displays connection information
- ✅ Handles MongoDB connection gracefully

**Configuration:**
- Port: Read from `app_portal/config.env` (default: 4100, can switch to 4200)
- Environment: Development mode
- Access: `http://localhost:4100` (or `http://localhost:4200` if switched)

### `launch-ref-skote.sh`

Launches the original Skote Nodejs v4.2.0 theme (Admin or Starterkit versions) or opens its documentation. This script is for **referencing the theme's design and structure**, not for running the Bifrost portal UI itself.

**Usage:**
```bash
./scripts/launch/launch-ref-skote.sh [admin|starterkit|docs]
```

**Options:**
- `admin`: Launches the full Admin version (default port 3000)
- `starterkit`: Launches the minimal Starterkit version (default port 3001, or 4100 if `config.env` is present from previous runs)
- `docs`: Opens the theme's documentation in your browser

**Example:**
```bash
./scripts/launch/launch-ref-skote.sh starterkit
```

Access the launched theme in your browser at `http://localhost:3001` (or the port specified in its `config.env`).

## Development Workflow

1.  **Launch Theme Reference (Optional)**:
    If you need to refer to the original Skote theme's design:
    ```bash
    ./scripts/launch/launch-ref-skote.sh starterkit
    ```
    (Access at `http://localhost:4100` if `app_portal/config.env` was previously updated by `launch-portal.sh` to 4100, otherwise 3001)

2.  **Launch Bifrost Portal UI**:
    ```bash
    ./scripts/launch/launch-portal.sh
    ```
    (Access at `http://localhost:4100` or `http://localhost:4200` if 4100 is busy)

3.  **Vue.js Conversion**:
    - Study EJS templates in `app_portal/views/` (from the copied Starterkit).
    - Convert to Vue.js components in `app_portal/src/components/` and `app_portal/src/pages/`.
    - Integrate with FastAPI backend via `app_portal/api.js`.

## Notes

- The `app_portal/` directory currently contains the Node.js/Express Starterkit code.
- This will be gradually replaced by Vue.js components as development progresses.
- `app_portal/api.js` is preserved for FastAPI integration.
- The Starterkit code in `app_portal/` is excluded from Git via `app_portal/.gitignore`.
- The original Skote theme package in `reference/` is also excluded from Git.
