#!/bin/bash
# Quick guide for passwordless sudo setup

echo "=========================================="
echo "Passwordless Sudo Setup Guide"
echo "=========================================="
echo ""
echo "To enable passwordless sudo on APP-SERVER:"
echo ""
echo "Method 1: Automated (recommended)"
echo "  ./setup-passwordless-sudo.sh"
echo ""
echo "Method 2: Manual (if automated doesn't work)"
echo "  1. ssh app-server"
echo "  2. sudo nano /etc/sudoers.d/bifrost-management"
echo "  3. Add: vision ALL=(ALL) NOPASSWD: /bin/systemctl, /usr/bin/journalctl, /usr/sbin/service"
echo "  4. Save and: sudo chmod 0440 /etc/sudoers.d/bifrost-management"
echo "  5. Verify: sudo visudo -c -f /etc/sudoers.d/bifrost-management"
echo ""
echo "See: setup-passwordless-sudo-manual.md for detailed instructions"
echo ""

