"""
Catalog data management.
Functions for importing and refreshing catalog data.
"""

import json
import csv
import io
from pathlib import Path
from typing import Any, Dict, List
from .loader import save_catalog, load_catalog
from .utils import normalize_brand_code

try:
    import requests
except Exception:
    requests = None


def ingest_catalog_csv(csv_path: str, mode: str = "merge") -> Dict[str, Any]:
    """
    Ingest a CSV file of colors into the local catalog.

    CSV columns: brand_code,brand,name,hex,url,lrv,hue_family,undertone_tags,collection,shade,finishes
    - undertone_tags is a semicolon-separated list
    - finishes is a semicolon-separated list
    - mode: "merge" (default) or "replace"
    """
    csv_file = Path(csv_path)
    if not csv_file.exists():
        return {"error": f"CSV not found: {csv_path}"}

    existing = [] if mode == "replace" else load_catalog()
    from .loader import create_catalog_index
    index = create_catalog_index(existing)

    added = 0
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            brand_code = normalize_brand_code(row.get("brand_code") or row.get("brand"))
            name = (row.get("name") or "").strip()
            if not brand_code or not name:
                continue
            entry = {
                "brand_code": brand_code,
                "brand": row.get("brand") or ("Benjamin Moore" if brand_code == "BM" else "Sherwin-Williams" if brand_code == "SW" else "Farrow & Ball" if brand_code == "FB" else brand_code),
                "name": name,
                "hex": (row.get("hex") or "").strip() or None,
                "url": (row.get("url") or "").strip() or None,
                "lrv": float(row["lrv"]) if (row.get("lrv") and row.get("lrv").strip()) else None,
                "hue_family": (row.get("hue_family") or "").strip() or None,
                "undertone_tags": [t.strip() for t in (row.get("undertone_tags") or "").split(";") if t.strip()],
                "collection": (row.get("collection") or "").strip() or None,
                "shade": (row.get("shade") or "").strip() or None,
                "finishes": [t.strip() for t in (row.get("finishes") or "").split(";") if t.strip()],
            }
            key = (brand_code, name)
            if key not in index:
                existing.append(entry)
                index[key] = entry
                added += 1

    save_catalog(existing)
    return {"ok": True, "added": added, "total": len(existing)}


def refresh_catalog_from_urls(urls: List[str], mode: str = "merge") -> Dict[str, Any]:
    """
    DEPRECATED: This function has been removed from the agent to prevent data corruption.
    It was causing the agent to wipe the catalog when validation failed.
    
    Fetch CSV or JSON catalog(s) from URLs and merge/replace local catalog.
    Only basic CSV/JSON parsing is supported. Remote failures are skipped.
    
    WARNING: This function can corrupt the catalog if URLs are invalid or return bad data.
    """
    if requests is None:
        return {"error": "requests not installed"}

    existing = [] if mode == "replace" else load_catalog()
    from .loader import create_catalog_index
    index = create_catalog_index(existing)
    added = 0

    for url in urls:
        try:
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            content_type = resp.headers.get("content-type", "").lower()
            text = resp.text
            # Try JSON first if content-type hints it or text begins with [ or {
            parsed_any = False
            if "application/json" in content_type or text.strip().startswith(("[", "{")):
                data = json.loads(text)
                if isinstance(data, dict):
                    items = data.get("items") or data.get("results") or []
                else:
                    items = data
                for row in items:
                    brand_code = normalize_brand_code(row.get("brand_code") or row.get("brand"))
                    name = (row.get("name") or "").strip()
                    if not brand_code or not name:
                        continue
                    entry = {
                        "brand_code": brand_code,
                        "brand": row.get("brand") or ("Benjamin Moore" if brand_code == "BM" else "Sherwin-Williams" if brand_code == "SW" else "Farrow & Ball" if brand_code == "FB" else brand_code),
                        "name": name,
                        "hex": (row.get("hex") or "").strip() or None,
                        "url": (row.get("url") or "").strip() or None,
                        "lrv": row.get("lrv"),
                        "hue_family": (row.get("hue_family") or "").strip() or None,
                        "undertone_tags": row.get("undertone_tags") or [],
                        "collection": (row.get("collection") or "").strip() or None,
                        "shade": (row.get("shade") or "").strip() or None,
                        "finishes": row.get("finishes") or [],
                    }
                    key = (brand_code, name)
                    if key not in index:
                        existing.append(entry)
                        index[key] = entry
                        added += 1
                parsed_any = True
            if not parsed_any:
                # Try CSV
                stream = io.StringIO(text)
                reader = csv.DictReader(stream)
                for row in reader:
                    brand_code = normalize_brand_code(row.get("brand_code") or row.get("brand"))
                    name = (row.get("name") or "").strip()
                    if not brand_code or not name:
                        continue
                    entry = {
                        "brand_code": brand_code,
                        "brand": row.get("brand") or ("Benjamin Moore" if brand_code == "BM" else "Sherwin-Williams" if brand_code == "SW" else "Farrow & Ball" if brand_code == "FB" else brand_code),
                        "name": name,
                        "hex": (row.get("hex") or "").strip() or None,
                        "url": (row.get("url") or "").strip() or None,
                        "lrv": float(row["lrv"]) if (row.get("lrv") and row.get("lrv").strip()) else None,
                        "hue_family": (row.get("hue_family") or "").strip() or None,
                        "undertone_tags": [t.strip() for t in (row.get("undertone_tags") or "").split(";") if t.strip()],
                        "collection": (row.get("collection") or "").strip() or None,
                        "shade": (row.get("shade") or "").strip() or None,
                        "finishes": [t.strip() for t in (row.get("finishes") or "").split(";") if t.strip()],
                    }
                    key = (brand_code, name)
                    if key not in index:
                        existing.append(entry)
                        index[key] = entry
                        added += 1
        except Exception:
            # Skip this URL on any error; continue others
            continue

    save_catalog(existing)
    return {"ok": True, "added": added, "total": len(existing)} 