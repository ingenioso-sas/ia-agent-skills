---
name: pigsty-target-manager
description: Use when adding, modifying, reloading, or auditing Prometheus and VictoriaMetrics scrape targets in Pigsty.
---

# Pigsty Target Manager

## Overview
Pattern for managing VictoriaMetrics scrape targets and reloading monitoring configurations in Pigsty without service interruption.

## When to Use
- When registering a new node's cAdvisor (`9338`), Node Exporter (`9100`), or app exporter in VictoriaMetrics.
- When configuring `prometheus_scrape_configs` or target files in `/infra/targets/`.
- When executing hot-reloads of VictoriaMetrics configurations via Pigsty playbooks.

When NOT to use:
- For creating Grafana visual panels (use `pigsty-dashboard-specialist` instead).

## Quick Reference
- **Config file:** `/opt/projects/pigsty-ing-basico/pigsty.yml`
- **Dynamic targets dir:** `/infra/targets/<category>/<node_name>.yml`
- **Reload command:** `./infra.yml -t vmetrics_config,vmetrics_launch -c local`

## Implementation

### 1. Dynamic Target File
Create `/infra/targets/<category>/<node_ip>.yml`:
```yaml
- targets:
    - <node_ip>:9338
  labels:
    job: cadvisor
    instance: <node_ip>
```

### 2. Scrape Config in `pigsty.yml`
Under `prometheus_scrape_configs`:
```yaml
- job_name: cadvisor
  metrics_path: /metrics
  scrape_interval: 15s
  max_scrape_size: 64MB
  scheme: http
  targets: ['<node_ip>:9338']
  labels:
    instance: <node_ip>
```

### 3. Hot Reload Execution
```bash
cd /opt/projects/pigsty-ing-basico
./infra.yml -t vmetrics_config,vmetrics_launch -c local
```

## Common Mistakes
- **Duplicate Scrape Targets:** Defining the same target in both `/infra/targets/` and `prometheus_scrape_configs` creates duplicate time series for every metric.
- **Generic Instance Label:** Setting `instance: "docker-containers"` prevents filtering panels by specific server IP. Use the actual node IP or hostname.
