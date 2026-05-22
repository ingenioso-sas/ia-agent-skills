---
name: odoo-13-development
description: Complete guide for Odoo 13 module development covering manifest structure, security, reports, wizards, data files, hooks, and exception handling.
globs: "**/*.{py,xml,csv}"
topics:
  - Module structure (folders and files)
  - __manifest__.py (all fields, qweb, external dependencies)
  - Security (access rights CSV, record rules, groups)
  - Reports (qweb-pdf, qweb-html, report actions, templates)
  - Wizards & TransientModel (structure, views, multi-step)
  - Data files (records, cron jobs, server actions)
  - Hooks (post_init, pre_init, uninstall)
  - Exception handling (UserError, AccessError, ValidationError, etc.)
  - Complete module examples
when_to_use:
  - Creating new Odoo modules
  - Configuring security and access rights
  - Building reports
  - Creating wizards/transient models
  - Setting up cron jobs and server actions
  - Writing module hooks
  - Handling exceptions properly
---

# Odoo 13 Development Guide

Complete guide for Odoo 13 module development: manifest structure, reports, security, wizards, and advanced patterns.

## Table of Contents

1. [Module Structure](#module-structure)
2. [__manifest__.py](#manifestpy)
3. [Security](#security)
4. [Reports](#reports)
5. [Wizards & Transient Models](#wizards--transient-models)
6. [Data Files](#data-files)
7. [Hooks](#hooks)
8. [Refactoring & Maintenance](#refactoring--maintenance)

---

## Module Structure

### Standard Module Structure

```
my_module/
├── __init__.py                 # Package init
├── __manifest__.py             # Module manifest (REQUIRED)
├── models/
│   ├── __init__.py
│   └── my_model.py             # Model definitions
├── views/
│   ├── my_model_views.xml      # View definitions
│   ├── my_model_templates.xml  # QWeb templates (Assets)
│   └── report_templates.xml    # Report templates
├── security/
│   ├── ir.model.access.csv     # Access rights (REQUIRED)
│   └── my_module_security.xml   # Record rules
├── data/
│   ├── my_module_data.xml      # Data records
│   └── ir_cron_data.xml        # Scheduled actions
├── demo/
│   └── my_module_demo.xml      # Demo data
├── report/
│   ├── my_report_views.xml     # Report actions
│   └── my_report_templates.xml # Report QWeb templates
├── wizard/
│   ├── __init__.py
│   ├── my_wizard.py            # TransientModel
│   └── my_wizard_views.xml     # Wizard views
├── static/
│   ├── src/
│   │   ├── js/                 # JavaScript files
│   │   ├── css/                # CSS files
│   │   ├── scss/               # SCSS files
│   │   └── xml/                # Static XML (JS Templates)
│   └── description/
│       └── icon.png            # Module icon
├── controllers/
│   ├── __init__.py
│   └── my_controller.py        # HTTP controllers
├── tests/
│   ├── __init__.py
│   └── test_my_module.py       # Test cases
```

---

## __manifest__.py

### Basic Manifest

```python
{
    'name': 'My Module',
    'version': '13.0.1.0.0',
    'summary': 'Short description of module',
    'description': """
Long Description
==================
Detailed description of what the module does.
    """,
    'category': 'My Category',
    'author': 'Your Name',
    'website': 'https://www.example.com',
    'license': 'LGPL-3',

    # Dependencies
    'depends': [
        'base',
        'product',
    ],

    # Data files
    'data': [
        'security/my_module_security.xml',
        'security/ir.model.access.csv',
        'views/my_module_views.xml',
        'views/my_module_templates.xml',
        'data/my_module_data.xml',
        'report/my_report_views.xml',
    ],

    # Demo data
    'demo': [
        'demo/my_module_demo.xml',
    ],

    # Static XML (JS Templates)
    'qweb': [
        'static/src/xml/*.xml',
    ],

    # Installation
    'installable': True,
    'application': False,
    'auto_install': False,

    # Hooks
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}
```

### Manifest Fields Reference

| Field | Description |
|-------|-------------|
| `name` | Module name |
| `version` | Version (e.g., `13.0.1.0.0`) |
| `depends` | Required module dependencies |
| `data` | Data files to load (XML, CSV) |
| `qweb` | Static XML templates for JavaScript |
| `demo` | Demo data files |
| `installable` | Whether module can be installed |
| `application` | Whether it's an app (shows in Apps menu) |

### Assets Declaration (Odoo 13)

In Odoo 13, assets are declared in XML templates, NOT in the manifest.

```xml
<!-- In views/my_module_templates.xml -->
<template id="assets_backend" name="my_module assets" inherit_id="web.assets_backend">
    <xpath expr="." position="inside">
        <link rel="stylesheet" href="/my_module/static/src/scss/my_style.scss"/>
        <script type="text/javascript" src="/my_module/static/src/js/my_script.js"></script>
    </xpath>
</template>
```

---

## Security

### Access Rights (ir.model.access.csv)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,base.group_user,1,1,1,0
access_my_model_manager,my.model.manager,model_my_model,group_my_module_manager,1,1,1,1
```

### Record Rules (ir.rule)

```xml
<record id="my_model_comp_rule" model="ir.rule">
    <field name="name">My Model multi-company</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[('company_id', 'in', company_ids)]</field>
    <field name="global" eval="True"/>
</record>
```

---

## Reports

### Report Action (ir.actions.report)

```xml
<record id="action_report_my_model" model="ir.actions.report">
    <field name="name">My Model Report</field>
    <field name="model">my.model</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">my_module.report_my_model</field>
    <field name="report_file">my_module.report_my_model</field>
    <field name="print_report_name">'My Model - %s' % (object.name)</field>
    <field name="binding_model_id" ref="model_my_model"/>
    <field name="binding_type">report</field>
</record>
```

### QWeb Report Template

```xml
<template id="report_my_model_document">
    <t t-call="web.external_layout">
        <div class="page">
            <h2 t-field="doc.name"/>
            <p>Date: <span t-field="doc.date"/></p>
        </div>
    </t>
</template>

<template id="report_my_model">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="doc">
            <t t-call="my_module.report_my_model_document" t-lang="doc.partner_id.lang"/>
        </t>
    </t>
</template>
```

---

## Wizards & Transient Models

### TransientModel Structure

```python
class MyWizard(models.TransientModel):
    _name = 'my.wizard'

    date = fields.Date(string='Date', default=fields.Date.today)
    
    def action_process(self):
        # Process logic
        return {'type': 'ir.actions.act_window_close'}
```

### Wizard View

```xml
<record id="view_my_wizard_form" model="ir.ui.view">
    <field name="name">my.wizard.form</field>
    <field name="model">my.wizard</field>
    <field name="arch" type="xml">
        <form string="My Wizard">
            <group>
                <field name="date"/>
            </group>
            <footer>
                <button string="Process" name="action_process" type="object" class="btn-primary"/>
                <button string="Cancel" class="btn-secondary" special="cancel"/>
            </footer>
        </form>
    </field>
</record>
```

---

## Data Files

### Cron Jobs

```xml
<record id="cron_my_model_cleanup" model="ir.cron">
    <field name="name">Clean up old records</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="state">code</field>
    <field name="code">model.cron_cleanup()</field>
    <field name="interval_number">1</field>
    <field name="interval_type">days</field>
    <field name="numbercall">-1</field>
</record>
```

---

## Hooks

```python
# In __init__.py or specific hook file
def post_init_hook(cr, registry):
    from odoo import api, SUPERUSER_ID
    env = api.Environment(cr, SUPERUSER_ID, {})
    # Hook logic
```

---


---

## Refactoring & Maintenance

To prevent regressions during refactoring (like the "ParseError: has no attribute" during updates), the following checklist is **mandatory** before finalizing any structural change:

1.  **XML Dependency Audit**: Before deleting or moving any Python method, perform a global search (`grep`) in the `data/` and `views/` directories. Check for `<function>`, `<button type="object">`, or `eval` calls that reference the method.
2.  **Initial Data Verification**: Methods like `init_csv_data` or `uninstall_custom_models` are often triggered by Odoo's internal registry during addon updates. They must remain in the base model or be explicitly imported in `__init__.py`.
3.  **Migration Testing**: Always attempt a dry-run update (`odoo-bin -u <module_name> --stop-after-init`) to ensure the `data.xml` files still parse correctly with the new architecture.


---

## Advanced Architecture: Mixins & Service Objects

For complex models (e.g., Localizations, EDI), avoid "God Objects". Use **Separation of Concerns**:

1.  **Model Fragmentation (Mixins)**: Split logic into specialized files using multiple inheritance (`_inherit`).
    *   `res_company.py`: Core fields.
    *   `res_company_onboarding.py`: UI and state logic.
    *   `res_company_api.py`: External integration glue.
2.  **Service Objects**: Move HTTP/Heavy logic to pure Python classes in `utils/`.
3.  **Encapsulation**: Models should delegate to services, not implement raw network logic.

## Exception Reference

### UserError

```python
from odoo.exceptions import UserError
raise UserError("Business error message")
```

### AccessError

```python
from odoo.exceptions import AccessError
raise AccessError("Insufficient permissions")
```

### ValidationError

```python
from odoo.exceptions import ValidationError
raise ValidationError("Data validation failed")
```

### RedirectWarning

```python
from odoo.exceptions import RedirectWarning
raise RedirectWarning("Message", action_id, "Button label")
```

---

**For more Odoo 13 guides, see [SKILL.md](../SKILL.md)**
