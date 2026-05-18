# PDFNameForger - Docker Setup

A Python program for analyzing and intelligently renaming PDF files with **provider-based configuration**.

## Features

✨ **Per-Provider Configuration** - Each invoice provider gets its own `.yml` configuration
📊 **Pattern-Matching** - Extracts variables from PDF text using Regex
📄 **Filename Variables** - Extract values from filenames as well
🔢 **Flexible Formatting** - Leading zeros, date formatting, free templates
🧪 **Dry-Run Mode** - Safely test before actual renaming
🐳 **Docker** - Development in an isolated, reproducible environment

## Structure

```
PDFNameForger/
├── Dockerfile              # Container definition
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Python dependencies
├── CONFIG_GUIDE.md         # Detailed configuration guide
├── scripts/               # Python code (volume)
│   ├── main.py           # Entry point
│   ├── config.py         # Configuration & loader
│   ├── pdf_processor.py  # PDF processing & pattern matching
│   └── renamer.py        # Renaming logic
├── config/               # Configuration files
│   ├── sim.de.yml        # Example: sim.de
│   └── TEMPLATE.yml      # Template for new providers
├── input/                # Input PDFs (volume)
└── output/               # Renamed PDFs (volume)
```

## Quick Start

### 1. Build Docker image
```bash
docker-compose build
```

### 2. Run container (Dry-Run)
```bash
docker-compose run --rm pdfnameforger
```

### 3. Process PDFs
1. Place PDF files in `input/`
2. Start the container
3. Check the console for proposed renames (Dry-Run mode)
4. If everything looks good: set `dry_run: false` in the configuration file

## Configuration

Each invoice provider gets a `.yml` file in `config/`:

```yaml
name: Telekom
file_pattern: "*.pdf"
output_format: "Telekom_{invoice_number}_{date}.pdf"
dry_run: true

variables:
  - name: invoice_number
    pattern: "Invoice-No\\.?:?\\s*(\\d+)"
    optional: false
    format_spec: "08d"  # 8-digit with leading zeros
  
  - name: date
    pattern: "Invoice Date[\\s:]*([\\d{1,2}[.\\-/]\\d{1,2}[.\\-/]\\d{4})"
    optional: false
    format_spec: "date:%Y-%m-%d"  # ISO date format
```

👉 **See [CONFIG_GUIDE.md](CONFIG_GUIDE.md) for detailed documentation!**

## Dependencies

| Package | Purpose |
|---------|---------|
| **pdfplumber** | Extract text from PDFs |
| **PyYAML** | Load configuration files |

## Development

### Code Changes
The `scripts/` folder is mounted - changes to code are visible immediately:

```bash
# Edit code
# Then restart the container:
docker-compose run --rm pdfnameforger
```

### Create New Configuration
```bash
# 1. Create new file: config/my_provider.yml
# 2. Add configuration (see CONFIG_GUIDE.md)
# 3. Start container
docker-compose run --rm pdfnameforger
```

### Interactive Work
```bash
# Start bash in container
docker-compose run -it --rm pdfnameforger bash

# Then e.g. test Python scripts:
python scripts/main.py
```

## Operating Modes

### 🧪 Dry-Run Mode (Default)
```yaml
dry_run: true
```
- Only show what WOULD be renamed
- No files are actually moved
- Perfect for testing new configurations

### ✅ Production Mode
```yaml
dry_run: false
```
- PDFs are actually renamed
- They are moved from `input/` to `output/`
- If file exists in `output/`, automatically append `_1`, `_2`, etc.

## Error Handling

| Situation | Behavior |
|-----------|----------|
| Required pattern not found | File is NOT renamed |
| Optional pattern not found | OK, is ignored |
| File with same name exists | Automatically append `_1`, `_2` suffix |
| PDF extraction fails | File is skipped |

## Format Specifications

The `format_spec` field allows you to transform extracted values. Here are all supported formats:

### Number Formatting (Integer Padding)

Add leading zeros to numbers using Python format specs:

```yaml
variables:
  - name: invoice_id
    pattern: "ID[\\s:]*([0-9]+)"
    format_spec: "05d"   # 5-digit with leading zeros: 123 → 00123
```

| Format | Result | Example |
|--------|--------|---------|
| `"03d"` | 3-digit with leading zeros | `7` → `007` |
| `"05d"` | 5-digit with leading zeros | `123` → `00123` |
| `"08d"` | 8-digit with leading zeros | `456` → `00000456` |
| `"010d"` | 10-digit with leading zeros | `789` → `0000000789` |

### Date Formatting

Parse dates from various input formats and output in any format:

```yaml
variables:
  - name: invoice_date
    pattern: "Date[\\s:]*([\\d{1,2}[.\\-/]\\d{1,2}[.\\-/]\\d{4})"
    format_spec: "date:%Y-%m-%d"
```

**Supported input formats (auto-detected):**
- `%d.%m.%Y` - German format (18.05.2024)
- `%d/%m/%Y` - Slash format (18/05/2024)
- `%Y-%m-%d` - ISO format (2024-05-18)
- `%d-%m-%Y` - Dash format (18-05-2024)

**Common output formats:**
| Format | Result |
|--------|--------|
| `"date:%Y-%m-%d"` | ISO format: `2024-05-18` |
| `"date:%d.%m.%Y"` | German format: `18.05.2024` |
| `"date:%Y%m%d"` | Compact: `20240518` |
| `"date:%d.%m."` | Short: `18.05.` |
| `"date:%B %Y"` | Full month: `May 2024` |
| `"date:%b %d, %Y"` | US format: `May 18, 2024` |
| `"date:%A, %d %B %Y"` | Full: `Friday, 18 May 2024` |

For all available date formats, see [Python strftime docs](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes).

### String Formatting

#### Remove Spaces
Remove all whitespace from extracted text:

```yaml
variables:
  - name: phone_number
    pattern: "Phone[\\s:]*([0-9\\-\\s]+)"
    format_spec: "remove_spaces"
```

Example: `0176 42 095 773` → `017642095773`

### Combining with Filename Template

Use formatted variables in your output filename:

```yaml
name: MyProvider
file_pattern: "*.pdf"
output_format: "{customer_id}_{invoice_date}_{amount}_{phone}.pdf"
dry_run: true

variables:
  - name: customer_id
    pattern: "Customer[\\s:]*([0-9]+)"
    format_spec: "08d"  # Padded to 8 digits
  
  - name: invoice_date
    pattern: "Date[\\s:]*([\\d{1,2}[.\\-/]\\d{1,2}[.\\-/]\\d{4})"
    format_spec: "date:%Y%m%d"  # YYYYMMDD format
  
  - name: amount
    pattern: "Total[\\s:]*([0-9.]+)"
    # No format_spec - use as-is
  
  - name: phone
    pattern: "Phone[\\s:]*([0-9\\-\\s]+)"
    format_spec: "remove_spaces"
```

**Example output:** `00012345_20240518_1234.56_017642095773.pdf`

## Tips

1. **Start with example configurations** - `sim.de.yml` is fully functional
2. **Test regex** - https://regex101.com/ (Python flavor)
3. **Always start with dry-run** - Before setting `dry_run: false`
4. **Check logs** - Container output shows exactly what happened

## Local Requirements (outside Docker)

```bash
python 3.11+
pip install -r requirements.txt
```

## Support

For configuration questions, see [CONFIG_GUIDE.md](CONFIG_GUIDE.md)  
For troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
