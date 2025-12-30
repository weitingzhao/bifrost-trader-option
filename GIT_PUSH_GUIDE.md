# Git Push Guide

## Current Status

- ✅ Repository is connected to: https://github.com/weitingzhao/bifrost-trader-option.git
- ✅ Local branch is ahead by 3 commits
- ❌ Push failed due to authentication (using wrong GitHub account)

## Issue

Git is trying to use account "ArchTech-Ghy" but needs to use "weitingzhao" account.

## Solutions

### Option 1: Use SSH (Recommended)

1. **Set up SSH key for weitingzhao account** (if not already):
   ```bash
   ssh-keygen -t ed25519 -C "your-email@example.com"
   # Add public key to GitHub: Settings > SSH and GPG keys
   ```

2. **Change remote to SSH**:
   ```bash
   git remote set-url origin git@github.com:weitingzhao/bifrost-trader-option.git
   ```

3. **Push**:
   ```bash
   git push -u origin main
   ```

### Option 2: Use Personal Access Token

1. **Create Personal Access Token** on GitHub:
   - Go to: https://github.com/settings/tokens
   - Generate new token (classic)
   - Select scopes: `repo` (full control)

2. **Push with token**:
   ```bash
   git push https://YOUR_TOKEN@github.com/weitingzhao/bifrost-trader-option.git main
   ```

   Or update remote:
   ```bash
   git remote set-url origin https://YOUR_TOKEN@github.com/weitingzhao/bifrost-trader-option.git
   git push -u origin main
   ```

### Option 3: Use GitHub CLI

```bash
# Install gh CLI if needed
brew install gh

# Authenticate
gh auth login

# Push
git push -u origin main
```

### Option 4: Update Git Credentials

```bash
# Clear cached credentials
git credential-osxkeychain erase
host=github.com
protocol=https

# Or use credential helper
git config --global credential.helper osxkeychain

# Then push (will prompt for credentials)
git push -u origin main
```

## Quick Fix

The easiest is to use SSH:

```bash
# Change to SSH URL
git remote set-url origin git@github.com:weitingzhao/bifrost-trader-option.git

# Push
git push -u origin main
```

## Verify

After pushing, verify on GitHub:
https://github.com/weitingzhao/bifrost-trader-option

