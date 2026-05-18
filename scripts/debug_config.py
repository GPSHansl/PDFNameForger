"""
Debug script to check loaded configuration
"""

from config import ConfigManager
from pathlib import Path

config_dir = Path("/app/config")
config_manager = ConfigManager(config_dir)

config = config_manager.get_config("sim.de")

if config:
    print(f"Provider: {config.name}")
    print(f"Variables:\n")
    for i, var in enumerate(config.variables, 1):
        print(f"{i}. {var.name}")
        print(f"   Pattern: {var.pattern[:50]}...")
        print(f"   Format Spec: {var.format_spec}")
        print(f"   Optional: {var.optional}")
        print()
