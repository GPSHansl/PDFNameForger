# PDFNameForger - Configuration Guide

## Overview

The PDFNameForger system allows you to automatically rename PDFs based on:
- **Pattern-Matching**: Extracts variables from PDF content using Regex
- **Formatting**: Leading zeros, date formatting, etc.
- **Validation**: Optional or required fields
- **Dry-Run Mode**: Safely test before actual renaming

## File Structure

```
config/
├── telekom.yml        # Example: Telekom invoices
├── sim.de.yml         # Example: sim.de invoices
└── my_provider.yml    # Your own configuration
```

## Configuration File Structure (YAML)

```yaml
# Unique provider name
name: ProviderName

# Wildcard pattern for files to process
# Examples: "*.pdf", "invoice_*.pdf", "invoice_2024_*.pdf"
file_pattern: "*.pdf"

# Format string for new filename
# {variable_name} is replaced with extracted values
output_format: "Provider_{invoice_number}_{date}.pdf"

# Dry-Run mode (true = only simulate renaming)
dry_run: true

# List of variables to extract
variables:
  - name: invoice_number
    pattern: "REGEX_PATTERN"
    optional: false          # true = variable can be missing
    format_spec: "FORMAT"    # Optional: formatting specification
```

## Pattern & Format-Spec Examples

### 1. Simple Text Extraction

```yaml
- name: supplier
  pattern: "(?:Supplier|Vendor)[\s:]*([A-Za-z0-9\s]+)"
  optional: false
```

**Regex explanation:**
- `(?:Supplier|Vendor)` - Matches "Supplier" OR "Vendor" (non-capturing group)
- `[\s:]*` - Any number of whitespace or colons
- `([A-Za-z0-9\s]+)` - Capturing group: One or more letters, numbers or whitespace

### 2. Numbers with Leading Zeros

```yaml
- name: invoice_number
  pattern: "Invoice-No\.?:?\s*(\d+)"
  format_spec: "08d"  # Format as 8-digit number with leading zeros
```

**Result:** `123` → `00000123`

### 3. Date Values

```yaml
- name: date
  pattern: "(?:Invoice Date|Date)[\s:]*([\d{1,2}[.\-/]\d{1,2}[.\-/]\d{4})"
  format_spec: "date:%Y-%m-%d"
```

**Input:** `18.05.2024` or `18-05-2024` or `18/05/2024`
**Output:** `2024-05-18`

**Supported input formats:** `%d.%m.%Y`, `%d/%m/%Y`, `%Y-%m-%d`, `%d-%m-%Y`
**Output format:** Any [Python strftime format](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes)

### 4. Optional Fields

```yaml
- name: amount
  pattern: "(?:Total Amount|Total)[\s:]*([0-9,.]+)"
  optional: true  # Field does NOT need to be present
```

If a **required field** (optional: false) is not found, the file is **NOT renamed**.

### 5. Extract Variables from Filename

```yaml
# Extract variables from filename (not from PDF content)
filename_variables:
  - name: invoice_number
    pattern: "B([0-9]+)\\.pdf"  # Regex with capturing group
    group: 1  # Which group to extract (1-based, default: 1)
    format_spec: "08d"  # Optional: formatting like PDF variables
```

**Example:** Filename `B623258454.pdf`
- Pattern: `"B([0-9]+)\\.pdf"`
- Group: 1
- Result: `623258454`

With `format_spec: "08d"` → `00623258`

## Regex Quick Reference

| Symbol | Meaning | Example |
|--------|---------|----------|
| `\d` | Digit | `\d{3}` = exactly 3 digits |
| `\w` | Letter/digit/_ | `\w+` = one or more |
| `[...]` | Character class | `[A-Z]` = uppercase letters |
| `+` | One or more | `\d+` = one or more digits |
| `*` | Zero or more | `\s*` = zero or more whitespace |
| `?` | Optional (0 or 1) | `\d?` = zero or one digit |
| `(...) ` | Capturing group | is extracted |
| `(?:...)` | Non-capturing group | is NOT extracted |
| `\|` | OR | `A\|B` = A or B |

## Format-Spec Reference

### Number Formatting
- `"05d"` → 5-digit with leading zeros (`123` → `00123`)
- `"08d"` → 8-digit with leading zeros
- `"03d"` → 3-digit with leading zeros

### Date Formatting
- `"date:%d.%m.%Y"` → Day.Month.Year (`18.05.2024`)
- `"date:%Y-%m-%d"` → ISO format (`2024-05-18`)
- `"date:%B %Y"` → Full month year (`May 2024`)
- `"date:%d.%m."` → Day.Month (`18.05.`)

## Praktische Beispiele

### Beispiel 1: Telekom Rechnung

```yaml
name: Telekom
file_pattern: "*.pdf"
output_format: "Telekom_{rechnungsnummer}_{datum}.pdf"
dry_run: true

variables:
  - name: rechnungsnummer
    pattern: "Rechnungs-Nr\.?:?\s*(\d+)"
    optional: false
    format_spec: "08d"
  
  - name: datum
    pattern: "(?:Rechnungsdatum)[\s:]*(\d{1,2}[.\-/]\d{1,2}[.\-/]\d{4})"
    optional: false
    format_spec: "date:%Y-%m-%d"
```

**Eingabe-PDF enthält:** 
```
Rechnungs-Nr: 123456
Rechnungsdatum: 18.05.2024
```

**Ergebnis:** `Telekom_00123456_2024-05-18.pdf`

### Beispiel 2: Vattenfall mit optionalen Feldern

```yaml
name: Vattenfall
file_pattern: "vattenfall_*.pdf"
output_format: "Vattenfall_{rechnungsnummer}_{monat}_{betrag}.pdf"
dry_run: true

variables:
  - name: rechnungsnummer
    pattern: "(?:Rechnungsnummer|Ref\.)[\s:]*([A-Z0-9]+)"
    optional: false
  
  - name: monat
    pattern: "Abrechnungsmonat[\s:]*(\d{2})"
    optional: false
    format_spec: "02d"
  
  - name: betrag
    pattern: "Gesamtbetrag[\s:]*([0-9]+)"
    optional: true  # OK wenn nicht vorhanden
```

### Beispiel 3: sim.de mit Dateiname-Variablen

```yaml
name: sim.de
file_pattern: "B[0-9]+\\.pdf"  # Regex pattern
output_format: "{kundennummer}_{telefonnummer}_{rechnungsdatum_yyyymmdd}_{originaldateiname}_Rechnung_{rechnungsdatum_ddmmyyyy}.pdf"
dry_run: true

# Variablen aus dem Dateinamen extrahieren
filename_variables:
  - name: dateiname_nummer
    pattern: "B([0-9]+)\\.pdf"  # Extrahiert die Nummer aus "B623258454.pdf"
    group: 1

# Variablen aus PDF-Inhalt extrahieren
variables:
  - name: kundennummer
    pattern: "(?:Kundennummer|Kundenr)[\s:]*([0-9]+)"
    optional: false
  
  - name: telefonnummer
    pattern: "(?:Telefon|Anschluss)[\s:]*([0-9\-\s]+)"
    optional: false
  
  - name: rechnungsdatum_yyyymmdd
    pattern: "(?:Rechnungsdatum|Datum)[\s:]*(\d{1,2}[.\-/]\d{1,2}[.\-/]\d{4})"
    optional: false
    format_spec: "date:%Y%m%d"  # YYYYMMDD format
  
  - name: rechnungsdatum_ddmmyyyy
    pattern: "(?:Rechnungsdatum|Datum)[\s:]*(\d{1,2}[.\-/]\d{1,2}[.\-/]\d{4})"
    optional: false
    format_spec: "date:%d.%m.%Y"  # DD.MM.YYYY format
```

**Eingabe:**
- Dateiname: `B623258454.pdf`
- PDF enthält: Kundennummer: 12345678, Telefon: 0176-42095773, Rechnungsdatum: 28.02.2023

**Ausgabe:** `12345678_0176-42095773_20230228_B623258454_Rechnung_28.02.2023.pdf`

**Erklärung:**
- `{kundennummer}` → 12345678 (aus PDF)
- `{telefonnummer}` → 0176-42095773 (aus PDF)
- `{rechnungsdatum_yyyymmdd}` → 20230228 (aus PDF, formatiert als YYYYMMDD)
- `{originaldateiname}` → B623258454 (automatisch aus Dateinamen)
- `{rechnungsdatum_ddmmyyyy}` → 28.02.2023 (aus PDF, formatiert als DD.MM.YYYY)

## Debugging: Test Regex Patterns

To test regex patterns, use [regex101.com](https://regex101.com/):

1. Open https://regex101.com/
2. Select "Python" as flavor
3. Enter your pattern (e.g. `Invoice-No\.?:?\s*(\d+)`)
4. Copy a few lines from the PDF content into "Test String"
5. Check if the extraction works

## Operation

### Dry-Run (Safe Test Mode)
```yaml
dry_run: true  # ONLY show, do NOT rename
```

### Production Mode (Real Renaming)
```yaml
dry_run: false  # Actually rename files
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| "Required pattern 'X' not found" | Regex doesn't match | Adjust/test regex pattern |
| "Unreplaced variables in template" | Variable doesn't exist | Add variable or remove from format |
| "Would rename to: ..." (Dry-Run) | Everything OK, in dry-run mode | Change to dry_run: false for actual renaming |
| "File already exists" | File already exists | System automatically adds `_1`, `_2` etc. suffix |

## Tips & Best Practices

✅ **Do:**
- Start with `dry_run: true` and check results
- Test regex on https://regex101.com/
- Use meaningful variable names
- Mark optional fields with `optional: true`

❌ **Don't:**
- Use overly specific regex (especially for dates)
- Test without Dry-Run
- Process large batches without prior testing
