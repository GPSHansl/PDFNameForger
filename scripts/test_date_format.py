"""
Debug script to test date formatting
"""

from pdf_processor import VariableExtractor

# Test cases
test_cases = [
    ("28.02.2023", "date:%Y%m%d", "20230228"),
    ("28.02.2023", "date:%d.%m.%Y", "28.02.2023"),
    ("28/02/2023", "date:%Y%m%d", "20230228"),
]

print("🔍 Date Formatting Test\n")

for date_str, format_spec, expected in test_cases:
    result = VariableExtractor._format_value(date_str, format_spec)
    status = "✓" if result == expected else "✗"
    print(f"{status} Input: '{date_str}' | Format: '{format_spec}'")
    print(f"  Expected: {expected}")
    print(f"  Got:      {result}")
    print()
