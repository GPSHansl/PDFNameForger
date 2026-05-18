"""
PDFNameForger - Main Renaming Logic
"""

from pathlib import Path
from typing import List, Tuple
import fnmatch
import re
import errno
import shutil
from config import ProviderConfig
from pdf_processor import PDFTextExtractor, VariableExtractor, FilenameVariableExtractor, FilenameFormatter

class PDFRenamer:
    """Handles PDF renaming based on provider configuration"""
    
    def __init__(self, input_dir: Path, output_dir: Path):
        self.input_dir = input_dir
        self.output_dir = output_dir
    
    def find_files(self, config: ProviderConfig) -> List[Path]:
        """Find PDF files matching the provider's file pattern (supports both fnmatch and regex)"""
        matching_files = []
        
        # Try to use pattern as regex if it contains regex characters
        is_regex = any(char in config.file_pattern for char in r'[]()+*?.^$|\\')
        
        for pdf_file in self.input_dir.glob("*"):
            if not pdf_file.is_file():
                continue
            
            # Try regex first if pattern looks like regex
            if is_regex:
                try:
                    if re.match(config.file_pattern, pdf_file.name):
                        matching_files.append(pdf_file)
                except re.error:
                    # If regex fails, fall back to fnmatch
                    if fnmatch.fnmatch(pdf_file.name, config.file_pattern):
                        matching_files.append(pdf_file)
            else:
                # Use fnmatch for simple patterns
                if fnmatch.fnmatch(pdf_file.name, config.file_pattern):
                    matching_files.append(pdf_file)
        
        return matching_files
    
    def process_file(self, pdf_file: Path, config: ProviderConfig) -> Tuple[bool, str]:
        """
        Process a single PDF file.
        
        Returns:
            Tuple of (success, message)
        """
        print(f"\n📄 Processing: {pdf_file.name}")
        
        # Extract variables from filename first
        print("  Extracting from filename...")
        filename_vars = FilenameVariableExtractor.extract_variables(pdf_file.name, config)
        
        # Extract text from PDF
        pdf_text = PDFTextExtractor.extract_text(pdf_file)
        if not pdf_text:
            return False, "Could not extract text from PDF"
        
        # Extract variables using patterns from PDF text
        print("  Extracting from PDF text...")
        variables, errors = VariableExtractor.extract_variables(pdf_text, config)
        
        if variables is None:
            message = f"Extraction failed: {'; '.join(errors)}"
            print(f"  ✗ {message}")
            return False, message
        
        # Merge filename variables with PDF variables (PDF variables take precedence)
        all_variables = {**filename_vars, **variables}
        
        # Add special variable: original filename without extension
        original_filename_no_ext = pdf_file.stem  # e.g., "B623258454" from "B623258454.pdf"
        all_variables['originaldateiname'] = original_filename_no_ext
        
        # Format new filename
        new_filename = FilenameFormatter.format_filename(config.output_format, all_variables)
        
        if new_filename is None:
            message = "Could not format filename"
            print(f"  ✗ {message}")
            return False, message
        
        print(f"  ✓ New filename: {new_filename}")
        
        if new_filename is None:
            message = "Could not format filename"
            print(f"  ✗ {message}")
            return False, message
        
        print(f"  ✓ New filename: {new_filename}")
        
        # In dry-run mode, just report what would happen
        if config.dry_run:
            print(f"  [DRY-RUN] Would rename to: {new_filename}")
            return True, f"Would rename to: {new_filename}"
        else:
            # Actually rename the file
            try:
                new_path = self.output_dir / new_filename
                # Avoid overwriting existing files
                if new_path.exists():
                    counter = 1
                    base_name = new_filename.rsplit('.', 1)[0] if '.' in new_filename else new_filename
                    ext = '.' + new_filename.rsplit('.', 1)[1] if '.' in new_filename else ''
                    while new_path.exists():
                        new_filename = f"{base_name}_{counter}{ext}"
                        new_path = self.output_dir / new_filename
                        counter += 1
                
                try:
                    pdf_file.rename(new_path)
                except OSError as e:
                    # Handle Docker bind mounts or other cross-device moves.
                    if e.errno == errno.EXDEV:
                        shutil.copy2(pdf_file, new_path)
                        pdf_file.unlink()
                    else:
                        raise
                print(f"  ✓ Renamed to: {new_filename}")
                return True, f"Renamed to: {new_filename}"
            except Exception as e:
                message = f"Error renaming file: {e}"
                print(f"  ✗ {message}")
                return False, message
    
    def process_provider(self, config: ProviderConfig) -> dict:
        """
        Process all files for a specific provider.
        
        Returns:
            Dictionary with processing statistics
        """
        print(f"\n{'='*60}")
        print(f"Processing provider: {config.name}")
        print(f"File pattern: {config.file_pattern}")
        print(f"Mode: {'DRY-RUN' if config.dry_run else 'ACTUAL RENAME'}")
        print(f"{'='*60}")
        
        # Find matching files
        files = self.find_files(config)
        
        if not files:
            print(f"No files matching pattern '{config.file_pattern}' found")
            return {
                'provider': config.name,
                'total': 0,
                'successful': 0,
                'failed': 0,
                'results': []
            }
        
        print(f"\nFound {len(files)} file(s) to process")
        
        results = []
        successful = 0
        failed = 0
        
        for pdf_file in files:
            success, message = self.process_file(pdf_file, config)
            results.append({
                'file': pdf_file.name,
                'success': success,
                'message': message
            })
            
            if success:
                successful += 1
            else:
                failed += 1
        
        return {
            'provider': config.name,
            'total': len(files),
            'successful': successful,
            'failed': failed,
            'results': results
        }
