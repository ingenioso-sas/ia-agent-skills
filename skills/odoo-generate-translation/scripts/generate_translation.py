#!/usr/bin/env python3
"""
Odoo Translation Export Helper Script.
This script helps automate exporting translation files (.po/.pot) for Odoo addons,
resolving database password and connection properties from odoo.conf or user prompts.
It also automatically translates untranslated terms for the specified language.
"""

import argparse
import os
import sys
import getpass
import json
import urllib.request
import urllib.parse
import subprocess

def parse_odoo_config(config_path):
    """
    Parses Odoo configuration file to find db properties.
    Odoo configurations are simple key-value pairs separated by '='.
    """
    config = {}
    if not os.path.exists(config_path):
        return config
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#') or line.startswith(';'):
                    continue
                # Skip section headers
                if line.startswith('[') and line.endswith(']'):
                    continue
                if '=' in line:
                    key, val = line.split('=', 1)
                    config[key.strip()] = val.strip()
    except Exception as e:
        print(f"Warning: Error reading config file {config_path}: {e}", file=sys.stderr)
        
    return config

def get_interactive_input(prompt, default=None):
    """Gets input from user with an optional default value."""
    if default:
        val = input(f"{prompt} [{default}]: ").strip()
        return val if val else default
    else:
        while True:
            val = input(f"{prompt}: ").strip()
            if val:
                return val
            print("This field is required. Please enter a value.")

def translate_text(text, target_lang='es', source_lang='en'):
    """Translates text using Google Translate's free API."""
    try:
        # Standardize target lang to 2-chars (e.g. es_CO -> es) for the API
        api_target = target_lang.split('_')[0].lower()
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": source_lang,
            "tl": api_target,
            "dt": "t",
            "q": text
        }
        query_string = urllib.parse.urlencode(params)
        req = urllib.request.Request(f"{url}?{query_string}", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            translated = "".join([part[0] for part in data[0] if part[0]])
            return translated
    except Exception as e:
        print(f"Warning: Translation failed for '{text}': {e}", file=sys.stderr)
        return ""

def translate_po_file(po_path, target_lang='es'):
    """Parses a PO file and translates empty msgstr lines."""
    if not os.path.exists(po_path):
        return
        
    print(f"\nTranslating untranslated terms in {po_path}...")
    
    with open(po_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    new_lines = list(lines)
    translated_count = 0
    
    for idx, line in enumerate(lines):
        if line.strip() == 'msgstr ""':
            # Find the corresponding msgid
            msgid_lines = []
            msgid_start_idx = -1
            
            # Go backwards to find msgid
            for j in range(idx - 1, -1, -1):
                prev_line = lines[j].strip()
                if prev_line.startswith('"') and prev_line.endswith('"'):
                    msgid_lines.insert(0, prev_line[1:-1])
                elif prev_line.startswith('msgid '):
                    first_msgid_part = prev_line[6:].strip()
                    if first_msgid_part.startswith('"') and first_msgid_part.endswith('"'):
                        msgid_lines.insert(0, first_msgid_part[1:-1])
                    msgid_start_idx = j
                    break
                else:
                    break
                    
            if msgid_start_idx != -1:
                raw_msgid = "".join(msgid_lines)
                unescaped_msgid = raw_msgid.replace('\\n', '\n').replace('\\"', '"').replace('\\t', '\t')
                
                if unescaped_msgid.strip():
                    translated_text = translate_text(unescaped_msgid, target_lang=target_lang)
                    if translated_text:
                        # Escape the translated text back to PO format
                        escaped_translated = translated_text.replace('\n', '\\n').replace('"', '\\"').replace('\t', '\\t')
                        new_lines[idx] = f'msgstr "{escaped_translated}"\n'
                        translated_count += 1
                        
    if translated_count > 0:
        with open(po_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"Successfully translated {translated_count} terms.")
    else:
        print("No untranslated terms found or translation failed.")

def main():
    parser = argparse.ArgumentParser(description="Generate/Export Odoo Addon Translation files.")
    parser.add_argument("-m", "--module", help="Odoo module/addon name to export translations for (e.g. l10n_co_edi_jorels_pos)")
    parser.add_argument("-a", "--addons-path", help="Addons path where the module is located (e.g. /mnt/extra-addons/pos/)")
    parser.add_argument("-d", "--database", help="Odoo database name (e.g. odoo13_prueba2)")
    parser.add_argument("-c", "--config", default="/etc/odoo/odoo.conf", help="Path to Odoo config file (default: /etc/odoo/odoo.conf)")
    parser.add_argument("-l", "--language", nargs='?', const='es', default=None, help="Language code (e.g., es). If specified without value, defaults to 'es'. If not specified, exports a .pot template.")
    parser.add_argument("-o", "--output", help="Optional output file path override")
    parser.add_argument("--db-host", help="Database host (default: from config, or fallback to 'db')")
    parser.add_argument("--db-port", help="Database port (default: from config, or fallback to '5432')")
    parser.add_argument("--db-user", help="Database user (default: from config, or fallback to 'odoo')")
    parser.add_argument("--db-password", help="Database password (will check config, if not found and not provided, prompts the user)")
    parser.add_argument("--python-path", default="/usr/lib/python3/venv/bin/python", help="Python binary path (default: /usr/lib/python3/venv/bin/python)")
    parser.add_argument("--odoo-bin", default="/usr/lib/python3/dist-packages/odoo/odoo-bin", help="Odoo-bin executable path (default: /usr/lib/python3/dist-packages/odoo/odoo-bin)")
    parser.add_argument("--logfile", default="/", help="Odoo logfile argument (default: /)")
    parser.add_argument("--interactive", action="store_true", help="Force interactive prompts for missing addon details")
    
    args = parser.parse_args()
    
    # 1. Parse config file
    config = parse_odoo_config(args.config)
    
    # Determine DB credentials (Arg overrides Config overrides Defaults)
    db_host = args.db_host or config.get("db_host") or "db"
    db_port = args.db_port or config.get("db_port") or "5432"
    db_user = args.db_user or config.get("db_user") or "odoo"
    
    # Get DB password
    db_password = args.db_password or config.get("db_password")
    
    # Check environment variables as well
    if not db_password:
        db_password = os.environ.get("PASSWORD") or os.environ.get("DB_PASSWORD")
        
    # If password is still not found, prompt the user
    if not db_password:
        print(f"Database password not found in config file ({args.config}) or environment.", file=sys.stderr)
        if sys.stdin.isatty():
            db_password = getpass.getpass("Please enter DB Password: ")
        else:
            db_password = input("Please enter DB Password: ").strip()
            
        if not db_password:
            print("Error: Database password is required to generate translations.", file=sys.stderr)
            sys.exit(1)
            
    # Resolve module, addons-path and database (interactively if needed/requested)
    module = args.module
    addons_path = args.addons_path
    database = args.database
    language = args.language
    
    is_interactive = args.interactive or not (module and addons_path and database)
    
    if is_interactive:
        print("\n--- Odoo Translation Exporter Settings ---")
        module = module or get_interactive_input("Odoo Module Name")
        addons_path = addons_path or get_interactive_input("Addons Path", "/mnt/extra-addons/pos/")
        database = database or get_interactive_input("Database Name", "odoo13_prueba2")
        if language is None and get_interactive_input("Generate for specific language? (y/n)", "n").lower() == 'y':
            language = get_interactive_input("Language code", "es")
        
    # Standardize addons-path (ensure trailing slash)
    if addons_path and not addons_path.endswith('/'):
        addons_path += '/'
        
    # Resolve output path
    output = args.output
    is_pot = False
    if not output:
        i18n_dir = os.path.join(addons_path, module, "i18n")
        if language:
            output = os.path.join(i18n_dir, f"{language}.po")
        else:
            output = os.path.join(i18n_dir, f"{module}.pot")
            is_pot = True
    else:
        if output.endswith('.pot'):
            is_pot = True
            
    # Ensure directory of output file exists
    output_dir = os.path.dirname(output)
    if output_dir and not os.path.exists(output_dir):
        print(f"Directory {output_dir} does not exist. Creating it...")
        os.makedirs(output_dir, exist_ok=True)

    # Odoo i18n-export only accepts .po, .csv, or .tgz as format.
    # If we need a .pot file, we export as .po first and rename it.
    odoo_export_path = output
    if is_pot:
        odoo_export_path = output[:-4] + '.po'

    # 2. Build the command arguments
    cmd = [
        args.python_path,
        args.odoo_bin,
        "--config", args.config,
        "--db_host", db_host,
        "--db_port", db_port,
        "--db_user", db_user,
        "--db_password", db_password,
        "-d", database,
        f"--addons-path={addons_path}",
        f"--modules={module}",
        f"--i18n-export={odoo_export_path}",
        f"--logfile={args.logfile}",
        "--stop-after-init"
    ]
    
    # If language is specified, add it to the Odoo export command
    if language:
        cmd.append(f"--language={language}")
    
    # Hide password in the print output
    printed_cmd = list(cmd)
    pass_idx = printed_cmd.index("--db_password") + 1
    printed_cmd[pass_idx] = "********"
    
    print("\nCommand to run:")
    print(" ".join(printed_cmd))
    print()
    
    if is_interactive:
        confirm = input("Run translation export now? (y/n) [y]: ").strip().lower()
        if confirm and confirm != 'y':
            print("Export cancelled.")
            sys.exit(0)
            
    # Run the command with exact environment (specifically GEVENT_SUPPORT and other variables)
    env = os.environ.copy()
    env["GEVENT_SUPPORT"] = "False"
    env["PYTEST_ADDOPTS"] = "--no-cov"
    
    # Run Odoo translation export
    try:
        print(f"Running translation export for module '{module}'...")
        res = subprocess.run(cmd, env=env, check=True)
        
        # Rename temporary .po back to .pot if needed
        if is_pot:
            if os.path.exists(odoo_export_path):
                os.replace(odoo_export_path, output)
            print(f"Success! Translation template (.pot) written to {output}")
        else:
            print(f"Success! Base translation file written to {output}")
            # If language is specified, translate the untranslated lines
            translate_po_file(output, target_lang=language)
            
    except subprocess.CalledProcessError as e:
        print(f"\nError: Odoo command failed with exit code {e.returncode}.", file=sys.stderr)
        sys.exit(e.returncode)
    except Exception as e:
        print(f"\nError executing command: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
