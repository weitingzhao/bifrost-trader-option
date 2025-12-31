# Fix Cursor Terminal Issue

## Problem
Getting error when running commands in Cursor terminal:
```
(eval):3: parse error near `cursor_snap_ENV_VARS...'
zsh:1: command not found: dump_zsh_state
```

## Root Cause
This is a Cursor IDE shell initialization issue. Cursor is trying to execute code in your shell config files (`.zshrc`, `.zprofile`, or `.zshenv`) that's causing a parse error.

## Solution 1: Fix Shell Configuration (Recommended)

1. **Check your shell config files** for Cursor-related code:
   ```bash
   # In Terminal.app (not Cursor), run:
   grep -n "cursor_snap" ~/.zshrc ~/.zprofile ~/.zshenv 2>/dev/null
   ```

2. **If found, comment out or remove** the problematic lines.

3. **Or create a clean `.zshrc`** that doesn't interfere with Cursor:
   ```bash
   # Backup current config
   cp ~/.zshrc ~/.zshrc.backup
   
   # Create minimal .zshrc
   cat > ~/.zshrc << 'EOF'
   # Minimal zsh config
   export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"
   EOF
   ```

4. **Restart Cursor** after making changes.

## Solution 2: Use Cursor's Source Control Panel (Easiest - No Terminal Needed)

1. Open **Source Control** panel in Cursor (left sidebar, branch icon)
2. Click `+` next to "Changes" to stage all
3. Enter commit message:
   ```
   Refactor Streamlit monitoring app and add API development guide
   
   - Created utils.py to consolidate shared functions
   - Removed duplicate code from app.py
   - Updated pages to import from utils.py
   - Renamed 'FastAPI Live Logs' to 'API Logs'
   - Added API development guide and changelog
   - Created API tracking script
   ```
4. Click checkmark (✓) to commit
5. Click `...` → "Push"

## Solution 3: Use System Terminal (Terminal.app)

Open **Terminal.app** (not Cursor's terminal) and run:

```bash
cd /Users/vision-mac-trader/Desktop/stocks/bifrost-trader-option
python3 commit_and_push.py
```

Or use the bash script:
```bash
bash commit_and_push.sh
```

## Solution 4: Use Python Script Directly

I've created `commit_and_push.py` that bypasses shell issues. Run it in **Terminal.app**:

```bash
cd /Users/vision-mac-trader/Desktop/stocks/bifrost-trader-option
python3 commit_and_push.py
```

## Solution 5: Change Cursor's Default Shell

1. Open Cursor Settings
2. Search for "terminal shell"
3. Change default shell from `zsh` to `/bin/bash`
4. Restart Cursor

## Quick Fix: Temporary Workaround

If you need to use Cursor terminal immediately, try:

1. **Restart Cursor** - Sometimes fixes temporary issues
2. **Clear terminal** - Close and reopen terminal panel
3. **Use different shell** - In terminal, type: `bash` (switches to bash temporarily)

## Recommended Approach

**Use Solution 2 (Source Control Panel)** - It's the easiest and doesn't require fixing the terminal issue. All git operations can be done through Cursor's UI.

## Files Created

- `commit_and_push.py` - Python script (bypasses shell)
- `commit_and_push.sh` - Bash script (for system terminal)
- `commit_and_push_clean.sh` - Clean bash script (minimal environment)

