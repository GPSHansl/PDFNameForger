# PDFNameForger - Troubleshooting Guide

## Häufige Probleme und Lösungen

### 1. "No files matching pattern found"

**Problem:** Container läuft, aber es werden keine Dateien verarbeitet.

**Lösungen:**
- ✅ Prüfe ob PDFs im `input/` Ordner sind
- ✅ Prüfe ob das `file_pattern` in der Konfiguration korrekt ist
  ```yaml
  file_pattern: "*.pdf"  # Alle PDF-Dateien
  file_pattern: "rech_*.pdf"  # Nur Dateien die mit "rech_" anfangen
  ```
- ✅ Prüfe ob die Dateiendung wirklich `.pdf` ist (case-sensitive auf Linux!)

### 2. "Required pattern 'X' not found"

**Problem:** Eine erforderliche Variable wurde nicht extrahiert, Datei wird nicht umbenannt.

**Lösungen:**
1. **Regex Pattern überprüfen:**
   - Nutze https://regex101.com/ (Python flavor)
   - Kopiere eine echte Zeile aus der PDF hinein
   - Prüfe ob dein Pattern matched

2. **PDF-Text extrahieren für Debug:**
   ```bash
   docker-compose run -it --rm pdf-renamer bash
   python
   >>> from pdf_processor import PDFTextExtractor
   >>> from pathlib import Path
   >>> text = PDFTextExtractor.extract_text(Path("/app/input/dateiname.pdf"))
   >>> print(text)
   ```

3. **Häufige Fehler:**
   - ❌ `"Rechnungs-Nr: (\d+)"` → `-` ist literal, nicht escaped
   - ✅ `"Rechnungs-Nr[\s:]*(\d+)"` → Flexibel mit Leerzeichen/Doppelpunkt
   - ❌ `"Datum (\d+\.\d+\.\d+)"` → Punkte sind special characters
   - ✅ `"Datum[\s:]*(\d{1,2}\.\d{1,2}\.\d{4})"` → Escaped Punkte

### 3. "Unreplaced variables in template"

**Problem:** Eine Variable im `output_format` existiert nicht.

**Beispiel:**
```yaml
output_format: "Anbieter_{rechnungsnummer}_{datuum}.pdf"  # Tippfehler!
variables:
  - name: rechnungsnummer
    ...
```

**Lösung:**
- Variablennamen in `output_format` müssen exakt mit `name:` in `variables` übereinstimmen
- Tippfehler prüfen!

### 4. Docker Image bauen schlägt fehl

**Problem:** `docker-compose build` gibt Fehler aus.

**Lösungen:**
- ✅ Prüfe ob Docker läuft: `docker ps`
- ✅ Prüfe ob `Dockerfile` im Projekt-Root ist
- ✅ Starte Docker Desktop neu (Windows/Mac)
- ✅ Alte Images löschen: `docker system prune`

### 5. Permission Denied bei Linux

**Problem:** "Permission denied" Fehler auf Linux.

**Lösung:**
```bash
# Berechtigungen fix:
chmod +x run.sh
```

### 6. Datei wird nicht umbenannt (Dry-Run funktioniert)

**Problem:** In Dry-Run Mode wird die Umbenennung angezeigt, mit `dry_run: false` passiert aber nichts.

**Lösungen:**
- ✅ Prüfe ob `dry_run: false` in der Konfiguration gesetzt ist
- ✅ Container neu starten nach Konfigurationsänderung
- ✅ Prüfe ob die Ausgabedatei bereits existiert (wird mit Suffix umbenannt)

### 7. PDF-Text ist leer/unlesbar

**Problem:** Text aus PDF kann nicht extrahiert werden (gescannte PDFs).

**Hintergrund:** `pdfplumber` kann nur Text aus Text-PDFs extrahieren, nicht aus gescannten Bildern.

**Lösungen:**
- ✅ Nutze OCR (z.B. Tesseract/pytesseract) - erfordert zusätzliche Konfiguration
- ✅ Prüfe ob die PDF wirklich Text enthält (öffne in Adobe Reader, versuche Text zu kopieren)
- ✅ Konvertiere gescannte PDFs mit OCR tool (z.B. IronPDF, DocuWare)

### 8. Container startet aber macht nichts

**Problem:** `docker-compose run --rm pdf-renamer` startet, zeigt aber keine Output.

**Lösungen:**
- ✅ Prüfe ob `scripts/main.py` verändert wurde
- ✅ Starte mit `-it` flag für interaktive Output:
  ```bash
  docker-compose run -it --rm pdf-renamer
  ```
- ✅ Prüfe Logs:
  ```bash
  docker-compose logs -f
  ```

### 9. Dateiname ist zu lang

**Problem:** Dateiname nach Formatierung ist zu lang (Windows: max 255 Zeichen).

**Lösung:**
- ✅ Verkürze das `output_format`
- ✅ Nutze Abkürzungen: `{rechnungsnummer}` statt `{rechnungsnummer_lang}`

### 10. "File already exists"

**Problem:** Datei mit gleichem Namen existiert bereits im Output-Ordner.

**Verhalten:** System erstellt automatisch Dateinamen mit Suffix:
- `file_001.pdf` → `file_001_1.pdf` → `file_001_2.pdf` etc.

**Lösungen:**
- ✅ Das ist normales Verhalten, kein Fehler
- ✅ Oder: Änder `output_format` um Duplikate zu vermeiden

## Debugging Tipps

### 1. Regex Pattern testen
```bash
docker-compose run -it --rm pdf-renamer python /app/scripts/test_patterns.py
```

Interaktiv Regex Patterns gegen PDF-Inhalte testen.

### 2. PDF-Text anschauen
```bash
docker-compose run -it --rm pdf-renamer bash
python
```

```python
from pdf_processor import PDFTextExtractor
from pathlib import Path

text = PDFTextExtractor.extract_text(Path("/app/input/datei.pdf"))
print(text[:500])  # Erste 500 Zeichen
```

### 3. Konfiguration prüfen
```bash
docker-compose run -it --rm pdf-renamer bash
python
```

```python
from config import ConfigManager
from pathlib import Path

mgr = ConfigManager(Path("/app/scripts/../config"))
config = mgr.get_config("Telekom")
print(f"Pattern: {config.file_pattern}")
print(f"Output format: {config.output_format}")
for var in config.variables:
    print(f"  - {var.name}: optional={var.optional}")
```

### 4. Logs speichern
```bash
# Output in Datei speichern
docker-compose run --rm pdf-renamer 2>&1 | tee debug.log
```

## Performance Tipps

### Bei vielen Dateien:

1. **Teile die Verarbeitung auf:**
   ```bash
   # Nur Telekom verarbeiten
   docker-compose run --rm pdf-renamer
   # (nur Telekom wird verarbeitet wenn nur telekom.yml in config/)
   ```

2. **Nutze spezifischere Patterns:**
   - ❌ `"*.pdf"` = alle Dateien
   - ✅ `"telekom_*.pdf"` = nur Telekom Dateien

3. **Prüfe PDF-Größen:**
   - Große PDFs mit vielen Seiten brauchen länger zum Parsen
   - Optimiere ggf. die PDF vor Verarbeitung

## Weitere Ressourcen

- 📖 [CONFIG_GUIDE.md](CONFIG_GUIDE.md) - Ausführliche Konfigurationsdoku
- 🔗 [regex101.com](https://regex101.com/) - Regex tester (wähle Python)
- 📚 [Python strftime](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes) - Datumsformat-Codes
- 🐳 [Docker Docs](https://docs.docker.com/compose/) - Docker Compose Dokumentation
