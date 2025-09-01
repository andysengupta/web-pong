## PDF to GPT to Excel CLI

Convert PDF pages into structured text using GPT Vision and export to Excel while preserving headings, paragraphs, and tables.

### Features
- Per-page PDF rendering to images (PyMuPDF)
- GPT Vision extraction to structured JSON (OpenAI API)
- Excel writer preserving structure (openpyxl)
- Resume-safe, page range selection, and rate limit friendly

### Setup

1. Python 3.10+
2. Create virtual environment and install dependencies:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

3. Configure environment:

- Set `OPENAI_API_KEY` in your environment or create a `.env` file:

```bash
OPENAI_API_KEY=sk-...
```

### Usage

```bash
python -m app.cli --pdf input.pdf --out output.xlsx --pages 1-5
```

Arguments:
- `--pdf`: Path to input PDF
- `--out`: Path to output Excel file
- `--pages`: Optional page selection, e.g. `1`, `3-7`, or `1,3,5-8`
- `--model`: Optional GPT model (default `gpt-4o-mini`)
- `--dpi`: Render DPI (default 200)
- `--overwrite`: Overwrite output if exists

### Structure Mapping

Each page is extracted into sections:
- headings: [{level, text}]
- paragraphs: [text]
- tables: [{caption?, headers[], rows[][]}]

These are written to Excel as one sheet per PDF page with clear formatting.

### Notes
- Keep DPI modest (150-200) for cost/performance.
- You can re-run with `--pages` to process specific pages only.
- The app caches rendered images in memory; no disk writes required.

### License
MIT
