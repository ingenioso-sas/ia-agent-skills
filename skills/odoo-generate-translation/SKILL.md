---
name: odoo-generate-translation
description: Use when generating translation files (.po) for Odoo addons, exporting translation terms from an Odoo database, or configuring translation scripts for custom modules.
---

# Odoo Generate Translation

## Overview
This skill provides a helper script and guidelines to generate translation `.po` (language specific) and `.pot` (templates) files for Odoo modules. It uses a Python venv environment and Odoo CLI options to perform the translation export safely, extracting parameters like database settings and passwords from the configuration file (`odoo.conf`) or prompt dialogs.

## When to Use
- When localizing Odoo addons into specific languages (e.g., Spanish, French).
- When exporting user-facing translatable strings defined in Python models (`_()`), JavaScript widgets (`_t()`), or XML views/QWeb templates into a `.po` or `.pot` file.
- When configuring launch setups for local debug environments for translation.

Do NOT use when:
- Exporting translation files manually via the web interface.
- Merging translations that do not require running the Odoo backend engine.

## Core Pattern

### Script Execution Commands

#### 1. Generate Translation Template (.pot)
If you run the script **without specifying a language**, it will export a `.pot` template and save it at `<addons_path>/<module>/i18n/<module>.pot`:
```bash
./scripts/generate_translation.py -m <module_name> -a <addons_path> -d <database_name>
```

#### 2. Generate and Auto-Translate Language File (.po)
If you **specify a language** (defaults to `es` if the flag is provided without a value), it will generate `<lang>.po` (e.g. `es.po`), matching existing translations Odoo knows, and automatically translate any untranslated terms (`msgstr ""`) in the file:
```bash
./scripts/generate_translation.py -m <module_name> -a <addons_path> -d <database_name> -l es
```

If the database password isn't specified in `odoo.conf` (e.g. at `/etc/odoo/odoo.conf`), the script prompts the user for it securely.

## Quick Reference

| Argument | Description | Default / Source |
|---|---|---|
| `-m`, `--module` | Name of the Odoo addon (e.g., `l10n_co_edi_jorels_pos`) | Required (or prompted) |
| `-a`, `--addons-path` | Path to custom addons folder (e.g., `/mnt/extra-addons/...`) | Required (or prompted) |
| `-d`, `--database` | Name of the target Odoo DB (e.g., `odoo13_prueba2`) | Required (or prompted) |
| `-c`, `--config` | Path to Odoo config file | `/etc/odoo/odoo.conf` |
| `-l`, `--language` | Language code (e.g. `es`). If omitted, generates `.pot` template. | `None` (generates template) |
| `-o`, `--output` | Explicit destination file path | Derived: `i18n/<module>.pot` or `i18n/<lang>.po` |

## Implementation

The underlying command executed by the script is structured as follows:

```bash
/usr/lib/python3/venv/bin/python /usr/lib/python3/dist-packages/odoo/odoo-bin \
  --config /etc/odoo/odoo.conf \
  --db_host db \
  --db_port 5432 \
  --db_user odoo \
  --db_password <PASSWORD> \
  -d <DATABASE> \
  --addons-path=<ADDONS_PATH> \
  --modules=<MODULE> \
  --i18n-export=<PO_FILE_PATH> \
  --logfile=/ \
  --stop-after-init \
  [--language=<LANG>]
```

> [!NOTE]
> The environment variable `GEVENT_SUPPORT` must be set to `False` and `PYTEST_ADDOPTS` to `--no-cov` to ensure the debugging environment is stable during translation exports.

## Common Mistakes

- **Incorrect Addons Path**: Providing an absolute path that does not contain the module being exported. Always check that the directory matches where the target addon folder resides.
- **Empty password in config**: If the configuration file `odoo.conf` is missing a `db_password` line, the Odoo server will fail to authenticate with PostgreSQL. The script resolves this by prompting the user interactively.
- **PO file directory missing**: Odoo will fail if the parent directories of the export path do not exist. The helper script automatically creates the `i18n/` subdirectory if it is not present.
