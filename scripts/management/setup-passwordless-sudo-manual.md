# Manual Passwordless Sudo Setup

To enable passwordless sudo for systemd commands on APP-SERVER, follow these steps:

## Option 1: Limited Commands (Recommended - More Secure)

This allows passwordless sudo only for specific commands needed for service management.

### Step 1: SSH to APP-SERVER

```bash
ssh app-server
```

### Step 2: Create Sudoers File

```bash
sudo nano /etc/sudoers.d/bifrost-management
```

### Step 3: Add This Content

```
vision ALL=(ALL) NOPASSWD: /bin/systemctl, /usr/bin/journalctl, /usr/sbin/service, /usr/bin/psql, /usr/bin/createdb, /usr/bin/dropdb, /bin/ls, /usr/bin/lsof, /bin/netstat, /usr/bin/ss
```

### Step 4: Set Permissions

```bash
sudo chmod 0440 /etc/sudoers.d/bifrost-management
```

### Step 5: Verify Syntax

```bash
sudo visudo -c -f /etc/sudoers.d/bifrost-management
```

Should output: `/etc/sudoers.d/bifrost-management: parsed OK`

## Option 2: Full Passwordless Sudo (Less Secure)

⚠️ **Warning**: This gives full sudo access without password. Use only if you trust the user completely.

```bash
ssh app-server
sudo nano /etc/sudoers.d/bifrost-management
```

Add:
```
vision ALL=(ALL) NOPASSWD: ALL
```

Then:
```bash
sudo chmod 0440 /etc/sudoers.d/bifrost-management
sudo visudo -c -f /etc/sudoers.d/bifrost-management
```

## Test Passwordless Sudo

After setup, test from your Mac:

```bash
# This should NOT ask for password
ssh app-server "sudo -n systemctl --version"

# This should work without password
ssh app-server "sudo systemctl status bifrost-api"
```

## What Commands Are Enabled (Option 1)

- `systemctl` - Service management
- `journalctl` - Log viewing
- `service` - Alternative service command
- `psql`, `createdb`, `dropdb` - Database management
- `ls`, `lsof`, `netstat`, `ss` - System inspection

## Security Notes

- The sudoers.d file is safer than editing `/etc/sudoers` directly
- Limited commands (Option 1) is more secure than full access
- The file must have 0440 permissions
- Always verify syntax with `visudo -c`

## Troubleshooting

### Syntax Error

If you get a syntax error:
```bash
sudo visudo -c -f /etc/sudoers.d/bifrost-management
```

Fix the syntax and try again.

### Still Asking for Password

1. Check file permissions: `ls -l /etc/sudoers.d/bifrost-management`
2. Should be: `-r--r-----` (0440)
3. Check syntax: `sudo visudo -c -f /etc/sudoers.d/bifrost-management`

### Remove Configuration

To remove passwordless sudo:
```bash
sudo rm /etc/sudoers.d/bifrost-management
```

