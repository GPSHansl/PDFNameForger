"""
Configuration validator
Validates configuration files before use.

Usage:
    python validate_config.py
"""

import re
from pathlib import Path
from config import ConfigManager, ProviderConfig

def validate_pattern(pattern: str) -> tuple[bool, str]:
    """Validate if a regex pattern is valid"""
    try:
        re.compile(pattern, re.IGNORECASE | re.MULTILINE)
        return True, "OK"
    except Exception as e:
        return False, str(e)

def validate_format_string(format_str: str) -> tuple[bool, str]:
    """Validate if format string looks correct"""
    # Check for valid template placeholders
    placeholders = re.findall(r'\{(\w+)\}', format_str)
    if not placeholders:
        return False, "No placeholders found in format string (should contain {variable_name})"
    return True, f"OK - Found placeholders: {placeholders}"

def validate_config_file(config: ProviderConfig) -> list[str]:
    """
    Validate a configuration file.
    Returns list of warnings/errors.
    """
    issues = []
    
    # Check name
    if not config.name:
        issues.append("❌ Config name is empty")
    
    # Check file_pattern
    if not config.file_pattern:
        issues.append("❌ file_pattern is empty")
    else:
        # Try to use it with fnmatch
        try:
            import fnmatch
            # Just test if it's valid fnmatch pattern
            fnmatch.filter(["test.pdf", "file_123.pdf"], config.file_pattern)
        except Exception as e:
            issues.append(f"❌ file_pattern is invalid: {e}")
    
    # Check output_format
    if not config.output_format:
        issues.append("❌ output_format is empty")
    else:
        valid, msg = validate_format_string(config.output_format)
        if not valid:
            issues.append(f"❌ output_format invalid: {msg}")
    
    # Check variables
    if not config.variables:
        issues.append("⚠️  No variables defined")
    
    required_vars = set()
    optional_vars = set()
    
    for var in config.variables:
        # Check name
        if not var.name:
            issues.append(f"❌ Variable has empty name")
            continue
        
        # Check pattern
        if not var.pattern:
            issues.append(f"❌ Variable '{var.name}': pattern is empty")
        else:
            valid, msg = validate_pattern(var.pattern)
            if not valid:
                issues.append(f"❌ Variable '{var.name}': regex invalid - {msg}")
        
        # Track required/optional
        if var.optional:
            optional_vars.add(var.name)
        else:
            required_vars.add(var.name)
    
    # Check filename_variables
    if config.filename_variables:
        for var in config.filename_variables:
            # Check name
            if not var.name:
                issues.append(f"❌ Filename variable has empty name")
                continue
            
            # Check pattern
            if not var.pattern:
                issues.append(f"❌ Filename variable '{var.name}': pattern is empty")
            else:
                valid, msg = validate_pattern(var.pattern)
                if not valid:
                    issues.append(f"❌ Filename variable '{var.name}': regex invalid - {msg}")
            
            # Track as optional variable
            optional_vars.add(var.name)
    
    # Check if all required variables are in output_format
    if config.output_format:
        format_placeholders = set(re.findall(r'\{(\w+)\}', config.output_format))
        missing = required_vars - format_placeholders
        if missing:
            issues.append(f"⚠️  Required variables not in output_format: {', '.join(missing)}")
        
        extra = format_placeholders - required_vars - optional_vars
        if extra:
            issues.append(f"⚠️  Variables in output_format not defined: {', '.join(extra)}")
    
    # Check format_specs
    for var in config.variables:
        if var.format_spec:
            # Validate format spec
            if var.format_spec.endswith('d'):
                try:
                    width = int(var.format_spec[:-1]) if var.format_spec[:-1] else 0
                    if width < 0:
                        issues.append(f"⚠️  Variable '{var.name}': invalid format_spec width")
                except ValueError:
                    issues.append(f"⚠️  Variable '{var.name}': invalid numeric format_spec")
            elif var.format_spec.startswith('date:'):
                # Just check if it looks reasonable
                if '%' not in var.format_spec:
                    issues.append(f"⚠️  Variable '{var.name}': date format_spec should contain % codes")
    
    return issues

def main():
    print("\n" + "="*70)
    print("✓ CONFIGURATION VALIDATOR")
    print("="*70)
    
    config_dir = Path("/app/scripts/../config")
    config_manager = ConfigManager(config_dir)
    
    providers = config_manager.list_providers()
    
    if not providers:
        print("\n⚠️  No configurations found!")
        return
    
    total_issues = 0
    
    for provider_name in providers:
        config = config_manager.get_config(provider_name)
        if not config:
            continue
        
        print(f"\n{'─'*70}")
        print(f"Provider: {config.name}")
        print(f"{'─'*70}")
        print(f"  Pattern: {config.file_pattern}")
        print(f"  Output:  {config.output_format}")
        print(f"  Mode:    {'DRY-RUN' if config.dry_run else 'LIVE'}")
        print(f"  Variables: {len(config.variables)}")
        
        issues = validate_config_file(config)
        
        if not issues:
            print(f"  ✅ Configuration is valid!")
        else:
            print(f"\n  Issues found ({len(issues)}):")
            for issue in issues:
                print(f"    {issue}")
            total_issues += len(issues)
    
    print(f"\n{'='*70}")
    if total_issues == 0:
        print("✅ All configurations are valid!")
    else:
        print(f"⚠️  Found {total_issues} issue(s)")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
