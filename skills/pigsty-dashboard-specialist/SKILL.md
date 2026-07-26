---
name: pigsty-dashboard-specialist
description: Use when creating, updating, provisioning, or persisting Grafana dashboards in Pigsty infrastructure.
---

# Pigsty Dashboard Specialist

## Overview
Rules and provisioning patterns for creating persistent, auto-loading Grafana dashboards in Pigsty.

## When to Use
- When creating a new Grafana dashboard JSON for Pigsty services.
- When ensuring dashboards automatically provision on new Pigsty node installations.
- When setting up reactive template variables (`$instance`, `$container`) in Grafana.

When NOT to use:
- For modifying raw Prometheus scrape metrics (use `pigsty-target-manager` instead).

## Quick Reference
- **Codebase JSON path:** `/opt/projects/pigsty-ing-basico/files/grafana/<category>/<dashboard_name>.json`
- **Live Provisioning path:** `/infra/dashboards/<category>/<dashboard_name>.json`
- **Prometheus Datasource UID:** `ds-prometheus`

## Implementation

### 1. Datasource Wiring
All queries must use the default Pigsty Prometheus UID:
```json
"datasource": {
  "type": "prometheus",
  "uid": "ds-prometheus"
}
```

### 2. Reactive Template Variables
- `$instance` (Node/Server IP):
  ```json
  "query": "label_values(container_last_seen{job=\"cadvisor\"}, instance)",
  "refresh": 1
  ```
- `$container` (Dynamic Container filter):
  ```json
  "query": "label_values(container_last_seen{job=\"cadvisor\", instance=~\"$instance\"}, name)",
  "refresh": 2
  ```

### 3. Automatic Provisioning Sync
Save dashboard JSON to BOTH locations for live rendering AND persistent auto-provisioning on new Pigsty nodes:
```bash
cp dashboard.json /opt/projects/pigsty-ing-basico/files/grafana/app/<name>.json
sudo cp dashboard.json /infra/dashboards/app/<name>.json
```

## Common Mistakes
- **PromQL Comparison in Brackets:** Placing numeric comparisons (`> 0`, `< 8000000000`) inside label matchers `{...}` causes 422 parser errors. Place comparisons outside `{...}`.
- **Static Datasource Names:** Using string `"VictoriaMetrics"` instead of `{ "type": "prometheus", "uid": "ds-prometheus" }` prevents template variables from resolving.
