---
name: process-cleanup
description: Use when auditing local Linux processes for memory or CPU cleanup candidates, especially to preserve i2p, Tor, Bitcoin, Syncthing, VM processes, active SSH/autossh bridges, and system services while suggesting graceful stop commands for non-essential apps or helpers.
---

# Process Cleanup

Audit the current process table and suggest safe, graceful cleanup commands. Treat the task as read-only unless the user explicitly asks you to close processes.

## Keep Running By Default

Do not suggest closing these unless the user explicitly overrides them:

- `i2p`, `i2pd`, `i2pd-daemon`
- `tor`
- `bitcoin`, `bitcoin-qt`, `bitcoind`
- `syncthing`
- system-required services
- active VM processes such as `qemu-system-x86_64`
- GUI apps the user says they are using, commonly `brave`, `sublime_text`, and `bitcoin-qt`
- bridge/tunnel processes used for the AI server or VM, including `autossh`, `ssh -N ai-bridge`, `ssh -N hermes-sandbox-bridge`, `ssh -N hermes-vm-bridge`, and local forwards to the AI server

## Workflow

1. Inspect memory and swap:

```bash
free -h
```

2. Read processes sorted by memory and CPU:

```bash
ps -eo pid,ppid,user,stat,%cpu,%mem,rss,comm,args --sort=-%mem
ps -eo pid,ppid,user,stat,%cpu,%mem,rss,comm,args --sort=-%cpu
```

3. If Docker is available, list running containers:

```bash
docker ps --format 'table {{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Command}}'
```

If Docker is unavailable or permission-blocked, continue without Docker details.

4. Classify processes into:

- Keep running
- Good candidates to close
- Optional/conditional cleanup
- Leave alone/system services

5. Provide graceful close commands grouped by risk and purpose.

## Stop Command Preferences

Prefer service/container/application-native shutdowns over killing PIDs:

- Docker containers: `docker stop <container>`
- Managed services: `sudo systemctl stop <service>` or app-specific commands such as `sudo tailscale down`
- Ordinary user apps: `kill -TERM <pid>` or targeted `pkill -TERM ...`
- Forceful fallback only: `kill -9 <pid>`, clearly labeled as last resort

## Common Candidates

Usually safe depending on whether the user uses them:

- `tailscaled`: suggest `sudo tailscale down` then `sudo systemctl stop tailscaled`
- OpenShell containers or `openshell-gateway`: suggest `docker stop <container>` first, then `kill -TERM <gateway-pid>` only if the gateway remains
- `virt-manager`: GUI manager only; suggest `kill -TERM <pid>` if the VM itself should keep running
- `diodon`: clipboard history; suggest `pkill -TERM diodon`
- `tracker-miner-fs-3`: GNOME file indexing; suggest `pkill -TERM -f tracker-miner-fs-3`
- `evolution-calendar-factory`, `evolution-source-registry`, `evolution-addressbook-factory`, `evolution-alarm-notify`: GNOME calendar/account helpers; suggest targeted `pkill -TERM -f ...` commands if unused
- `goa-daemon`: GNOME Online Accounts; suggest `pkill -TERM goa-daemon` if unused
- `nautilus`: file manager service; suggest `kill -TERM <pid>` if no file browser is needed
- `mousepad` or other small editors: suggest `kill -TERM <pid>` if the user is done with them

Be cautious with:

- `gjs`: inspect command line. Desktop icons (`ding@rastersoft.com`) can be optional; GNOME notifications/screensaver helpers should usually be left alone.
- `plugin_host-*`: Sublime Text plugin hosts. Do not recommend killing them alone unless a plugin is stuck; suggest closing Sublime if the user wants that memory back.
- `dockerd` and `containerd`: only recommend stopping them if no required containers are running and the user does not need Docker.
- SSH/autossh bridges: keep if used for AI server or VM access.

## Response Shape

Return a concise report with:

- Current memory and swap state
- Top memory/CPU contributors
- Safe first batch to close
- Optional cleanup
- Processes intentionally kept
- Commands to close each candidate gracefully

Briefly explain why `kill -TERM`, `pkill -f`, service stop commands, and `kill -9` differ when recommending commands.
