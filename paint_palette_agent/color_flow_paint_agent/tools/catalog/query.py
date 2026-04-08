"""
Catalog query functionality.
Provides the main query_catalog function for filtering colors by criteria.
"""

from typing import Any, Dict, List
from .loader import load_catalog


def query_catalog(criteria: Dict[str, Any]) -> Dict[str, Any]:
    """
    Filter local paint catalog based on simple criteria.
    Now optimized for Farrow & Ball catalog only.

    Parameters
    ----------
    criteria : dict with optional keys
        - undertone: Optional[str] e.g. "warm", "cool", "neutral", "green", "blue"
        - hue_family: Optional[str] e.g. "gray", "white", "green", "blue"
        - lrv_min: Optional[float]
        - lrv_max: Optional[float]
        - collection: Optional[str] e.g. "Archive", "Signature", "New"
        - shade: Optional[str] e.g. "Light", "Mid", "Dark"
        - finish: Optional[str] e.g. "Estate Emulsion", "Modern Emulsion"
        - limit: Optional[int] number of items to return (default 5)

    Returns
    -------
    { "results": [ ... ] }
    Each item contains brand, name, hex, url, lrv (if any), undertone_tags.
    """
    catalog = load_catalog()
    if not catalog:
        return {"results": []}

    # No brand filtering needed - all colors are Farrow & Ball
    undertone = (criteria.get("undertone") or "").lower().strip()
    hue_family = (criteria.get("hue_family") or "").lower().strip()
    lrv_min = criteria.get("lrv_min", 0)
    lrv_max = criteria.get("lrv_max", 100)
    collection = (criteria.get("collection") or "").lower().strip()
    shade = (criteria.get("shade") or "").lower().strip()
    finish = (criteria.get("finish") or "").lower().strip()
    limit = int(criteria.get("limit", 5))

    def matches(entry: Dict[str, Any]) -> bool:
        if undertone and undertone not in [t.lower() for t in entry.get("undertone_tags", [])]:
            return False
        entry_hue_family = entry.get("hue_family")
        if hue_family and hue_family != (entry_hue_family.lower() if entry_hue_family else ""):
            return False
        entry_collection = entry.get("collection")
        if collection and collection != (entry_collection.lower() if entry_collection else ""):
            return False
        entry_shade = entry.get("shade")
        if shade and shade != (entry_shade.lower() if entry_shade else ""):
            return False
        if finish:
            finishes = [f.lower() for f in entry.get("finishes", [])]
            if finish not in finishes:
                return False
        lrv = entry.get("lrv")
        if isinstance(lrv, (int, float)):
            if lrv < lrv_min or lrv > lrv_max:
                return False
        return True

    filtered = [e for e in catalog if matches(e)]

    # Sort by LRV closeness to requested range, then by name for consistency
    mid_lrv = (lrv_min + lrv_max) / 2.0
    def score(entry: Dict[str, Any]) -> tuple:
        lrv = entry.get("lrv")
        lrv_dist = abs((lrv if isinstance(lrv, (int, float)) else mid_lrv) - mid_lrv)
        name = entry.get("name", "")
        return (lrv_dist, name)

    filtered.sort(key=score)
    return {"results": filtered[:limit]} 