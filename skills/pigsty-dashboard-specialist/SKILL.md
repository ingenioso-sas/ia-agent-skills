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
- `Custom Variables (Key/Value mapping)`:
  If defining a custom variable with a `query` string, the syntax in Grafana is `Texto Mostrado : Valor Interno`. Example:
  ```json
  "query": "Por Contenedor : name, Por Aplicacion : stack_name"
  ```

### 3. Automatic Provisioning Sync
Save dashboard JSON to BOTH locations for live rendering AND persistent auto-provisioning on new Pigsty nodes:
```bash
cp dashboard.json /opt/projects/pigsty-ing-basico/files/grafana/app/<name>.json
sudo cp dashboard.json /etc/dashboards/app/<name>.json
```

### 4. Hot Reloading (API Push)
If the dashboard already exists in Grafana's database, updating the file in `/etc/dashboards/app/` will **NOT** immediately apply changes. You MUST push the JSON via the Grafana API:
```python
import json, requests
with open('/opt/projects/pigsty-ing-basico/files/grafana/app/dashboard.json') as f:
    d = json.load(f)
payload = {"dashboard": d["dashboard"], "overwrite": True, "folderId": 0}
requests.post("http://127.0.0.1:3005/ui/api/dashboards/db", 
              auth=("admin", "pJGbLD8N9eO5qKEzE0OgRQRf"), json=payload)
```
*(Note: Pigsty's native `grafana.py init` script may fail due to SSL certs; bypass this by calling the local `3005` port HTTP endpoint directly as above).*

## Common Mistakes
- **PromQL Comparison in Brackets:** Placing numeric comparisons (`> 0`, `< 8000000000`) inside label matchers `{...}` causes 422 parser errors. Place comparisons outside `{...}`.
- **Parentheses matching with `by ()`:** `(sum(metric) by (var)) > 0` is correct. `(sum((metric) by (var)) > 0` is incorrect and causes `unexpected token "by"`.
- **Static Datasource Names:** Using string `"VictoriaMetrics"` instead of `{ "type": "prometheus", "uid": "ds-prometheus" }` prevents template variables from resolving.
