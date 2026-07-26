---
name: pigsty-app-specialist
description: Use when registering, creating, or deploying Docker Compose applications (such as cAdvisor, Vector, Odoo, Metabase, PgWeb) in Pigsty infrastructure.
---

# Pigsty App Specialist

## Overview
Standardized pattern for packaging and deploying Docker Compose applications within the native Pigsty app directory structure (`/app/<app_name>` and `/conf/app/`).

## When to Use
- When adding a new Docker component or container stack to a Pigsty cluster.
- When creating native `./app.yml` manifests for automated deployment.
- When organizing application Makefiles and Compose specs according to Pigsty conventions.

When NOT to use:
- For raw PostgreSQL extension installation (use `pgsql` roles instead).
- For uncontainerized system services.

## Quick Reference
- **App directory:** `/opt/projects/pigsty-ing-basico/app/<app_name>/`
- **Config manifest:** `/opt/projects/pigsty-ing-basico/conf/app/<app_name>.yml`
- **Deployment command:** `./app.yml -e app=<app_name> -l <target_node>`

## Implementation

### 1. Directory Setup
Create `/opt/projects/pigsty-ing-basico/app/<app_name>/` containing:
- `docker-compose.yml` (Compose specification)
- `Makefile` (Execution targets)

### 2. Required Makefile Targets
```makefile
default: up

up:
	docker compose up -d

stop:
	docker compose down

clean:
	docker compose down -v

.PHONY: default up stop clean
```

### 3. Config Manifest
Create `/opt/projects/pigsty-ing-basico/conf/app/<app_name>.yml`:
```yaml
<app_name>:
  name: <app_name>
  path: app/<app_name>
```

### 4. Execution
```bash
./app.yml -e app=<app_name> -l <target_node>
```

## Common Mistakes
- **Missing Makefile:** Running `./app.yml` will fail if no `Makefile` with an `up` target exists in `/app/<app_name>/`.
- **Container Name Conflicts:** Ensure `container_name` in `docker-compose.yml` does not conflict with existing running containers.
