---
name: pigsty-log-cache-cleaner
description: Use when disk space is low, journald logs grow large, or vmalert/VictoriaMetrics CPU usage requires optimization on Pigsty nodes.
---

# Pigsty Log & Cache Cleaner

## Overview
Maintenance patterns and scripts for managing disk space, journald retention, syslog rotation, and monitoring CPU overhead in Pigsty.

## When to Use
- When root partition `/` disk usage is high due to journalctl or Docker cache.
- When setting up persistent journald limits or logrotate rules on Pigsty nodes.
- When optimizing `vmalert` evaluation intervals to reduce CPU usage.

When NOT to use:
- For database vacuuming or PostgreSQL internal table bloat (use `pgsql` vacuum utilities).

## Quick Reference
- **Cleanup CLI:** `/opt/projects/pigsty-ing-basico/bin/clean-cache`
- **Cleanup Playbook:** `./clean.yml -c local`
- **Journal Limit:** `/etc/systemd/journald.conf.d/00-journal-limit.conf`

## Implementation

### 1. Execute Automated Cleanup
```bash
/opt/projects/pigsty-ing-basico/bin/clean-cache
```

### 2. Journald Retention Limit
Create `/etc/systemd/journald.conf.d/00-journal-limit.conf`:
```ini
[Journal]
SystemMaxUse=200M
MaxRetentionSec=1month
```
Restart journald: `sudo systemctl restart systemd-journald`

### 3. vmalert CPU Overhead Optimization
In `/opt/projects/pigsty-ing-basico/pigsty.yml`:
```yaml
vmalert_options: "-evaluationInterval=30s"
```
Reload: `./infra.yml -t vmalert_config,vmalert_launch -c local`

## Common Mistakes
- **Deleting Active Backups:** Never delete tarballs or backup files in production without explicit confirmation.
- **Unconstrained Scrape Sizes:** High metric volume from large exporters can cause VictoriaMetrics buffer overflows unless `-promscrape.maxScrapeSize=64MB` is set in `pigsty.yml`.
