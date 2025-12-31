# Quick Commit Guide

## ⚡ Fastest Method: Use Cursor's Source Control Panel

1. **Click the Source Control icon** in left sidebar (branch icon)
2. **Stage all changes**: Click `+` next to "Changes" (or press `Cmd+Shift+A`)
3. **Enter commit message**:
   ```
   Refactor Streamlit monitoring app and add API development guide
   ```
4. **Click checkmark (✓)** to commit
5. **Click `...` menu** → Select "Push"

**Done!** No terminal needed.

---

## Alternative: Use System Terminal

Open **Terminal.app** (not Cursor's terminal) and run:

```bash
cd /Users/vision-mac-trader/Desktop/stocks/bifrost-trader-option
python3 commit_and_push.py
```

This will automatically:
- Stage all changes
- Commit with descriptive message
- Push to GitHub

---

## Why Cursor Terminal Doesn't Work

Cursor's terminal has a shell initialization issue that prevents commands from running. The error `cursor_snap_ENV_VARS` is a Cursor IDE bug, not your code.

**Solution**: Use Cursor's Source Control panel or your system terminal instead.

