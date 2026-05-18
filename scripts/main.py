"""
PDFNameForger - Main Script
Analyzes PDF files and renames them based on their content.
"""

import sys
from pathlib import Path

# Add scripts directory to path
scripts_dir = Path("/app/scripts")
sys.path.insert(0, str(scripts_dir))

from config import ConfigManager
from renamer import PDFRenamer

def print_header():
    print("\n" + "="*70)
    print(" " * 15 + "🔄 PDF RENAMER - CONFIGURATION-BASED RENAMING")
    print("="*70)

def main():
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    config_dir = Path("/app/config")
    
    print_header()
    print(f"\n📂 Input Directory:  {input_dir}")
    print(f"📂 Output Directory: {output_dir}")
    print(f"📂 Config Directory: {config_dir}")
    
    # Erstelle Verzeichnisse, falls sie nicht existieren
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load configurations
    print("\n🔧 Loading provider configurations...")
    config_manager = ConfigManager(config_dir)
    
    providers = config_manager.list_providers()
    if not providers:
        print("⚠️  No provider configurations found!")
        print(f"   Place .yml files in {config_dir}")
        return
    
    print(f"✓ Found {len(providers)} provider(s): {', '.join(providers)}")
    
    # Process each provider
    renamer = PDFRenamer(input_dir, output_dir)
    
    total_stats = {
        'total_files': 0,
        'total_successful': 0,
        'total_failed': 0
    }
    
    for provider_name in providers:
        config = config_manager.get_config(provider_name)
        if config:
            stats = renamer.process_provider(config)
            
            total_stats['total_files'] += stats['total']
            total_stats['total_successful'] += stats['successful']
            total_stats['total_failed'] += stats['failed']
    
    # Print summary
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    print(f"Total files processed:  {total_stats['total_files']}")
    print(f"✓ Successful:           {total_stats['total_successful']}")
    print(f"✗ Failed:               {total_stats['total_failed']}")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
