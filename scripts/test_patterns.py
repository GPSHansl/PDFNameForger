"""
Utility script to test regex patterns against sample text.
Useful for debugging and developing new configurations.

Usage:
    python test_patterns.py
"""

import re
from pathlib import Path

def test_patterns():
    """Interactive pattern testing"""
    print("\n" + "="*70)
    print("🔍 PDF PATTERN TESTER")
    print("="*70)
    print("\nTest your regex patterns here before using them in config files!")
    print("(Type 'quit' to exit)\n")
    
    while True:
        print("-" * 70)
        pattern = input("Enter regex pattern (or 'quit' to exit): ").strip()
        
        if pattern.lower() == 'quit':
            print("\n✓ Exiting pattern tester")
            break
        
        if not pattern:
            print("⚠️  Empty pattern, try again")
            continue
        
        try:
            compiled = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
            print("✓ Regex is valid")
        except Exception as e:
            print(f"✗ Regex error: {e}")
            continue
        
        print("\nEnter text to search in (paste PDF excerpt, empty line ends input):")
        print("(Paste your text, press Enter twice to finish)")
        lines = []
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        
        text = "\n".join(lines)
        
        if not text:
            print("⚠️  Empty text, try again")
            continue
        
        matches = compiled.findall(text)
        search = compiled.search(text)
        
        print("\n" + "-" * 70)
        print(f"Text length: {len(text)} characters")
        
        if search:
            print(f"✓ Match found!")
            print(f"\nFirst match:")
            print(f"  Full match: '{search.group(0)}'")
            if search.groups():
                for i, group in enumerate(search.groups(), 1):
                    print(f"  Group {i}: '{group}'")
            print(f"\n  → Would extract: '{search.group(1) if search.groups() else search.group(0)}'")
        else:
            print("✗ No match found")
        
        print(f"\nTotal matches: {len(matches)}")
        if matches:
            print("All matches:")
            for i, match in enumerate(matches, 1):
                if isinstance(match, tuple):
                    print(f"  {i}. {match[0] if match else match}")
                else:
                    print(f"  {i}. {match}")

if __name__ == "__main__":
    test_patterns()
