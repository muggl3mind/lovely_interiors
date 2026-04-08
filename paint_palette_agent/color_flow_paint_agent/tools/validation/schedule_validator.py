"""
Paint schedule validation.
Validates paint schedules against the catalog and provides detailed debugging.
"""

from typing import Any, Dict, List, Optional
from ..catalog.loader import load_catalog
from ..catalog.utils import normalize_brand_code, is_similar_name


def validate_schedule(schedule: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced validation that provides detailed debugging information
    and prevents defensive behavior by being completely transparent.

    Returns
    -------
    { "ok": bool, "errors": [str], "unknowns": [ {brand_code,name,location} ], 
      "debug_info": [str], "catalog_stats": dict }
    """
    catalog = load_catalog()
    from ..catalog.loader import create_catalog_index
    index = create_catalog_index(catalog)
    errors: List[str] = []
    unknowns: List[Dict[str, str]] = []
    debug_info: List[str] = []
    
    # Add debug information about what we're validating
    debug_info.append(f"Validating against catalog with {len(index)} colors")
    farrow_ball_count = len([k for k in index.keys() if k[0] == "FB"])
    debug_info.append(f"Farrow & Ball colors available: {farrow_ball_count}")
    
    for room in schedule.get("rooms", []):
        room_name = room.get('name', 'Room')
        debug_info.append(f"Checking room: {room_name}")
        
        for key in ("walls", "trim", "ceiling", "alternate"):
            color_pick = room.get(key)
            if not color_pick:
                continue
                
            # Log exactly what we're trying to validate
            brand = color_pick.get("brand") or color_pick.get("brand_code")
            name = color_pick.get("name", "")
            debug_info.append(f"  {key}: Checking '{brand}' '{name}'")
            
            err = validate_pick(color_pick, index)
            if err:
                errors.append(f"{room_name}: {err}")
                unknowns.append({
                    "brand_code": normalize_brand_code(brand),
                    "name": name.strip(),
                    "location": f"{room_name} {key}"
                })
                
                # Add specific debugging for this failure
                debug_info.append(f"    FAILED: {err}")
            else:
                debug_info.append(f"    OK: Found in catalog")
    
    return {
        "ok": len(errors) == 0, 
        "errors": errors, 
        "unknowns": unknowns,
        "debug_info": debug_info,  # New: Full transparency
        "catalog_stats": {         # New: Catalog verification
            "total_colors": len(index),
            "farrow_ball_colors": farrow_ball_count
        }
    }


def validate_pick(p: Optional[Dict[str, Any]], index: Dict[tuple, Dict[str, Any]]) -> Optional[str]:
    """Validate a single color pick against the catalog index."""
    if not p:
        return None
    
    brand_val = p.get("brand") or p.get("brand_code")
    name_val = p.get("name")
    brand_code = normalize_brand_code(brand_val)
    name = (name_val or "").strip()
    
    if not brand_code or not name:
        return f"Missing brand or name: {p!r}"
    
    if (brand_code, name) not in index:
        # Look for similar colors to provide helpful suggestions
        suggestions = []
        name_lower = name.lower()
        
        # Check if the name contains codes that should be removed
        if any(code in name for code in [" HC-", " OC-", " No. ", " (", ")"]):
            # Try to find the base name without codes
            base_name = name
            
            # First handle parenthetical codes like "Color Name (HC-173)" or "Color Name (No. 295)"
            if "(" in base_name:
                paren_pos = base_name.find("(")
                potential_base = base_name[:paren_pos].strip()
                if potential_base:  # Make sure we don't end up with empty string
                    base_name = potential_base
            
            # Then handle space-separated codes like "Color Name HC-173"
            else:
                for pattern in [" HC-", " OC-", " No. "]:
                    if pattern in base_name:
                        base_name = base_name.split(pattern)[0].strip()
                        break
            
            if (brand_code, base_name) in index:
                return f"Unknown color: {brand_code} {name}. Try using just '{base_name}' without the code."
        
        # Look for partial matches and fuzzy matches
        for key in index.keys():
            if key[0] == brand_code:
                catalog_name_lower = key[1].lower()
                # Exact substring match
                if name_lower in catalog_name_lower:
                    suggestions.append(key[1])
                # Fuzzy match for typos (simple Levenshtein-like check)
                elif len(suggestions) < 3 and is_similar_name(name_lower, catalog_name_lower):
                    suggestions.append(key[1])
                if len(suggestions) >= 3:
                    break
        
        error_msg = f"Unknown color: {brand_code} {name}"
        if suggestions:
            error_msg += f". Similar colors found: {', '.join(suggestions)}"
        else:
            # Enhanced message for colors that might exist but aren't in catalog
            error_msg += f". This color may exist in the real world but isn't in our catalog. Please search our catalog using search_colors_smart() or query_catalog() to find available alternatives with similar characteristics. DO NOT attempt to refresh the catalog."
        return error_msg

    return None 