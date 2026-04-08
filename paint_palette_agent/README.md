## Color Flow Paint Agent — AI-Powered Paint Consultation System

**Goal**: A sophisticated multi-agent system that conducts professional paint consultations, analyzes room photos using computer vision, and generates room-by-room paint schedules with expert color recommendations.

**Launch**: Run with ADK Web (`adk web`) from this folder.

### Project Structure
```
paint_palette_agent/
├── README.md
├── pyproject.toml
├── main.py
├── .env.example
├── data/
│   ├── catalogs.json          # Professional paint database (301+ colors)
│   ├── samples/                # Sample room photos for testing
│   └── scripts/                # Data processing and import utilities
└── color_flow_paint_agent/
    ├── agent.py               # Main agent orchestration
    ├── prompt.py              # Expert knowledge and instructions
    ├── requirement_tracker.py # User requirement management
    └── tools/                 # Modular tool system
        ├── analysis/          # Computer vision & lighting
        ├── catalog/           # Paint database management
        ├── export/            # Professional schedule generation
        ├── recommendations/   # Color theory algorithms
        ├── search/            # Semantic color search
        └── validation/        # Quality assurance
```

### Intake flow
- Asks for rooms, style adjectives, warm/cool preference, trim/ceiling strategy, sheens.
- Accepts photo uploads per room (JPEG/PNG). If no photos, continues with text-only mode.

### Photo handling (MVP)
- Uses a vision-capable model to review images during intake.
- Extracts qualitative lighting cues (bright/dim, warm/cool cast) and notes dominant fixed finishes.
- If EXIF/time is missing, rely on filename labels like living_morning.jpg.

### Catalog + Selection Logic
- `data/catalogs.json` contains professional paint database with brand, name, hex values, URLs, LRV values, and undertone classifications.
- **Extensible schema**: Optional fields include `collection` (e.g., Heritage, Modern), `shade` (Light/Mid/Dark), and `finishes` (available finish types).
- **Smart selection algorithms**:
  - 1–2 base neutrals aligned with lighting warmth and LRV optimization.
  - Per-room complement/accent colors informed by existing finishes and design style.
  - Flow continuity: intelligent color repetition across adjacent spaces with depth variation.
  - Professional sheen recommendations: walls eggshell, trim semi-gloss, ceiling flat.

### Core Tools
- `query_catalog(criteria)` → filters local catalog by brand priority, undertone, LRV range, hue family; now also by `collection`, `shade`, and `finish`.
- `estimate_lighting(photo_filenames)` → qualitative tags for brightness/warmth (MVP stub).
- `validate_schedule(schedule)` → rejects colors not in the catalog.
- `export_schedule(schedule)` → saves a `.txt` summary only after validation passes.
- `ingest_catalog_csv(csv_path, mode)` → merges or replaces catalog from CSV with extended fields.
- `refresh_catalog_from_urls(urls, mode)` → merges or replaces catalog from remote CSV/JSON sources.

### Browser Automation Tools
- `order_paint_samples(colors, debug_mode)` → automated paint sample ordering via Browser-Use v0.7+ integration
  - AI-driven browser automation that adapts to website structure changes
  - Vision-based navigation with intelligent error recovery
  - Adds samples to cart and provides total price estimation
  - Stops at cart review for secure user-controlled purchase completion
  - Extensible to multiple paint retailer websites

### Export Tools
All paint schedules can be exported through the standard `export_schedule()` function for professional contractor use.

### Output Example
**Professional Paint Schedule:**
- **Living Room**
  - Walls: [Brand] "Warm Neutral Gray" — Premium Eggshell
  - Trim: [Brand] "Soft White" — Semi-Gloss
  - Ceiling: [Brand] "Soft White" — Flat
  - Alternate: [Brand] "Deeper Gray" (for accent wall consideration)
- **Kitchen**
  - Walls: [Brand] "Warm Stone" — Washable Finish
  - Accent: [Brand] "Muted Sage Green" — Eggshell
  - Trim/Ceiling: As above

*Includes color codes, LRV values, undertone notes, and application recommendations.*

### Configure
- Copy `.env.example` to `.env` and set your required API key:
  - GOOGLE_API_KEY=your_key

### Install and run
- Create and activate a virtual environment (recommended).
- Install dependencies:
  - pip install -e .
  - pip install -r requirements.txt  # For browser automation
  - playwright install  # For Browser-Use automation
- Start ADK Web UI from this folder:
  - adk web
- In your browser, select `color_flow_paint_agent` and chat. Upload room photos when prompted.

### Notes
- All processing is local aside from LLM calls.
- The mockup (visual repaint) is not enabled in Phase 1.
- You can expand `data/catalogs.json` over time to improve matches or import from CSV/JSON using the provided tools.
- /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="/tmp/chrome-debug-profile"
^ Use that to start persistent browser