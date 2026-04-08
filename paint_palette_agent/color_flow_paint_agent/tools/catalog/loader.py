"""
Catalog loading and saving utilities.
Handles the core functionality for managing the paint catalog data.
"""

import json
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
CATALOGS_DIR = DATA_DIR / "catalogs"

# Use the complete catalog with all hex, LRV, and description data (301 colors)
CATALOG_PATH = CATALOGS_DIR / "farrow_ball_complete.jsonl"


def load_catalog() -> List[Dict[str, Any]]:
    """
    Load the complete Farrow & Ball catalog from JSONL file.
    
    This catalog contains 301 unique colors with complete data:
    - All hex codes
    - All LRV values (calculated from hex)
    - All descriptions from F&B website
    - Hue families and undertone tags
    
    Returns:
        List of color dictionaries, empty list if file doesn't exist
    """
    if not CATALOG_PATH.exists():
        return []
    
    colors = []
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                colors.append(json.loads(line))
    
    return colors


def save_catalog(entries: List[Dict[str, Any]]) -> None:
    """
    Save the paint catalog to JSONL file (one JSON object per line).
    
    Args:
        entries: List of color dictionaries to save
    """
    CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def create_catalog_index(catalog: List[Dict[str, Any]] = None) -> Dict[tuple, Dict[str, Any]]:
    """
    Create an index of the catalog for fast lookups.
    
    Args:
        catalog: Optional catalog list, loads from file if not provided
        
    Returns:
        Dictionary mapping (brand_code, name) tuples to color entries
    """
    if catalog is None:
        catalog = load_catalog()
    
    index: Dict[tuple, Dict[str, Any]] = {}
    for entry in catalog:
        from .utils import normalize_brand_code  # Import here to avoid circular imports
        brand_code = normalize_brand_code(entry.get("brand_code") or entry.get("brand"))
        name = (entry.get("name") or "").strip()
        if brand_code and name:
            index[(brand_code, name)] = entry
    return index 