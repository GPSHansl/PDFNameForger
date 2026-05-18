"""
PDFNameForger - PDF text extraction and variable processing
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pdfplumber

from config import ProviderConfig


class PDFTextExtractor:
    """Extracts plain text from PDF files."""

    @staticmethod
    def extract_text(pdf_file: Path) -> Optional[str]:
        """Read all page text from a PDF file."""
        try:
            with pdfplumber.open(pdf_file) as pdf:
                pages = [page.extract_text() or "" for page in pdf.pages]
            text = "\n".join(pages).strip()
            return text or None
        except Exception as exc:
            print(f"  ✗ Error reading PDF '{pdf_file.name}': {exc}")
            return None


class VariableExtractor:
    """Extracts configured variables from PDF text."""

    _DATE_INPUT_FORMATS = [
        "%d.%m.%Y",
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%d-%m-%Y",
    ]

    @staticmethod
    def extract_variables(pdf_text: str, config: ProviderConfig) -> Tuple[Optional[Dict[str, str]], List[str]]:
        """Extract variables using regex patterns from provider config."""
        extracted: Dict[str, str] = {}
        errors: List[str] = []

        for variable in config.variables:
            match = re.search(variable.pattern, pdf_text, re.IGNORECASE | re.MULTILINE)

            if not match:
                if not variable.optional:
                    errors.append(f"Required pattern '{variable.name}' not found")
                continue

            raw_value = (match.group(1) if match.groups() else match.group(0)).strip()
            formatted = VariableExtractor._format_value(raw_value, variable.format_spec)

            if formatted is None:
                if not variable.optional:
                    errors.append(
                        f"Could not format variable '{variable.name}' with format '{variable.format_spec}'"
                    )
                continue

            extracted[variable.name] = formatted

        if errors:
            return None, errors

        return extracted, errors

    @staticmethod
    def _format_value(value: str, format_spec: Optional[str]) -> Optional[str]:
        """Apply formatting rules defined in config format_spec."""
        value = value.strip()

        if not format_spec:
            return value

        if format_spec == "remove_spaces":
            return re.sub(r"\s+", "", value)

        if format_spec.startswith("date:"):
            output_fmt = format_spec.split(":", 1)[1]
            normalized = value.replace("-", ".").replace("/", ".")

            for in_fmt in VariableExtractor._DATE_INPUT_FORMATS:
                try:
                    date_obj = datetime.strptime(normalized, in_fmt)
                    return date_obj.strftime(output_fmt)
                except ValueError:
                    continue
            return None

        # Python format spec (e.g., 08d) for numeric values
        try:
            numeric_value = int(value)
            return format(numeric_value, format_spec)
        except (TypeError, ValueError):
            pass

        # Fallback to generic string formatting
        try:
            return format(value, format_spec)
        except (TypeError, ValueError):
            return None


class FilenameVariableExtractor:
    """Extracts configured variables from source filename."""

    @staticmethod
    def extract_variables(filename: str, config: ProviderConfig) -> Dict[str, str]:
        """Extract filename variables and apply optional formatting."""
        extracted: Dict[str, str] = {}

        for variable in config.filename_variables:
            match = re.search(variable.pattern, filename)
            if not match:
                continue

            try:
                raw_value = match.group(variable.group).strip()
            except IndexError:
                continue

            formatted = VariableExtractor._format_value(raw_value, variable.format_spec)
            if formatted is not None:
                extracted[variable.name] = formatted

        return extracted


class FilenameFormatter:
    """Formats and sanitizes output filenames from templates."""

    _WINDOWS_FORBIDDEN_CHARS = r'[<>:"/\\|?*]'

    @staticmethod
    def format_filename(template: str, variables: Dict[str, str]) -> Optional[str]:
        """Render template with variables and return a filesystem-safe filename."""
        try:
            rendered = template.format(**variables)
        except KeyError:
            return None

        # Protect against invalid path characters.
        safe_name = re.sub(FilenameFormatter._WINDOWS_FORBIDDEN_CHARS, "_", rendered)
        safe_name = safe_name.strip().strip(".")

        return safe_name or None