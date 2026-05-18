"""
Configuration handling for invoice providers
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class PatternVariable:
    """Represents a pattern to extract from PDF text"""
    name: str
    pattern: str
    optional: bool = False
    format_spec: Optional[str] = None  # z.B. "05d" für führende Nullen
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PatternVariable':
        return cls(
            name=data['name'],
            pattern=data['pattern'],
            optional=data.get('optional', False),
            format_spec=data.get('format_spec')
        )

@dataclass
class FilenameVariable:
    """Represents a pattern to extract from filename"""
    name: str
    pattern: str  # Regex pattern with capturing groups
    group: int = 1  # Which group to extract (1-based)
    format_spec: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FilenameVariable':
        return cls(
            name=data['name'],
            pattern=data['pattern'],
            group=data.get('group', 1),
            format_spec=data.get('format_spec')
        )

@dataclass
class ProviderConfig:
    """Configuration for a specific invoice provider"""
    name: str
    file_pattern: str  # Wildcard pattern (e.g., "*.pdf")
    output_format: str  # Format string for renaming (e.g. "{rechnungsnummer}_{datum}.pdf")
    variables: List[PatternVariable]
    filename_variables: List[FilenameVariable] = None
    dry_run: bool = True
    
    def __post_init__(self):
        if self.filename_variables is None:
            self.filename_variables = []
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProviderConfig':
        variables = [
            PatternVariable.from_dict(var) 
            for var in data.get('variables', [])
        ]
        filename_variables = [
            FilenameVariable.from_dict(var)
            for var in data.get('filename_variables', [])
        ]
        return cls(
            name=data['name'],
            file_pattern=data['file_pattern'],
            output_format=data['output_format'],
            variables=variables,
            filename_variables=filename_variables,
            dry_run=data.get('dry_run', True)
        )

class ConfigManager:
    """Manages provider configurations"""
    
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.configs: Dict[str, ProviderConfig] = {}
        self._load_configs()
    
    def _load_configs(self):
        """Load all provider configurations from config directory"""
        if not self.config_dir.exists():
            print(f"Config directory {self.config_dir} does not exist")
            return
        
        for config_file in self.config_dir.glob("*.yml"):
            if config_file.name.startswith("_"):
                continue
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data:
                        config = ProviderConfig.from_dict(data)
                        self.configs[config.name] = config
                        print(f"✓ Loaded config: {config.name}")
            except Exception as e:
                print(f"✗ Error loading {config_file.name}: {e}")
    
    def get_config(self, provider_name: str) -> Optional[ProviderConfig]:
        """Get configuration for a specific provider"""
        return self.configs.get(provider_name)
    
    def list_providers(self) -> List[str]:
        """List all available providers"""
        return list(self.configs.keys())
