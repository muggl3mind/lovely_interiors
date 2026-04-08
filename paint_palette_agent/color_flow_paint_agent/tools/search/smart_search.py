"""
Smart color search functionality - REDESIGNED VERSION
Enhanced semantic understanding with better intent parsing.

REVISION NOTES:
- Previous version used simplistic keyword matching ("kitchen" → tag as kitchen)
- Previous version missed synonyms and context
- Previous version couldn't handle negation ("NOT like beige I have")

NEW APPROACH:
- Enhanced synonym recognition
- Better contextual understanding
- Pattern-based intent extraction
- More sophisticated query parsing

Note: This tool is CALLED BY the LLM agent, so we don't recursively call
the LLM here. Instead, we provide robust text analysis that the LLM's
natural language output can map to effectively.
"""

from typing import Any, Dict, List, Optional
from ..catalog.loader import load_catalog
from .matching import calculate_match_score, explain_match


def _strip_color_codes(name: str) -> str:
    """
    Strip color codes from color names to enable flexible searching.
    E.g., "Light Gray No. 17" → "Light Gray"
          "Hale Navy HC-154" → "Hale Navy"
    """
    if not name:
        return name
    
    # Handle parenthetical codes like "Color Name (HC-173)" or "Color Name (No. 295)"
    if "(" in name:
        paren_pos = name.find("(")
        potential_base = name[:paren_pos].strip()
        if potential_base:
            return potential_base
    
    # Handle space-separated codes like "Color Name HC-173" or "Color Name No. 17"
    for pattern in [" HC-", " OC-", " No. ", " No."]:
        if pattern in name:
            return name.split(pattern)[0].strip()
    
    return name


def search_colors_smart(query: str, criteria: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Enhanced color search with sophisticated intent parsing.
    
    Args:
        query: Color search - can be exact name or natural language description
        criteria: Optional additional filters
    
    Returns:
        Dictionary with ranked color results and explanations
    """
    catalog = load_catalog()
    if not catalog:
        return {"results": [], "error": "No catalog found"}
    
    query_clean = query.strip()
    
    # Strip out color codes if present
    query_stripped = _strip_color_codes(query_clean)
    
    # STRATEGY 1: Exact name match (highest priority)
    for search_term in [query_clean, query_stripped]:
        if not search_term:
            continue
        exact_matches = [c for c in catalog if c.get('name', '').lower() == search_term.lower()]
        if exact_matches:
            return {
                "results": exact_matches,
                "search_strategy": "exact_name_match",
                "total_matches": len(exact_matches),
                "explanation": f"Found exact match for '{query}'"
            }
    
    # STRATEGY 2: Partial name match (second priority)
    for search_term in [query_clean, query_stripped]:
        if not search_term:
            continue
        partial_matches = [c for c in catalog if search_term.lower() in c.get('name', '').lower()]
        if partial_matches:
            # Sort by name length (shorter = better match) and LRV
            partial_matches.sort(key=lambda x: (len(x.get('name', '')), -x.get('lrv', 50)))
            return {
                "results": partial_matches[:10],
                "search_strategy": "partial_name_match", 
                "total_matches": len(partial_matches),
                "explanation": f"Found {len(partial_matches)} colors with '{query}' in the name"
            }
    
    # STRATEGY 3: Fuzzy name matching (for typos)
    fuzzy_matches = []
    for color in catalog:
        color_name = color.get('name', '').lower()
        if len(query_clean) > 3 and len(color_name) > 3:
            common_chars = sum(1 for c in query_clean.lower() if c in color_name)
            similarity = common_chars / max(len(query_clean), len(color_name))
            if similarity > 0.7:  # 70% character overlap
                fuzzy_matches.append((color, similarity))
    
    if fuzzy_matches:
        fuzzy_matches.sort(key=lambda x: x[1], reverse=True)
        return {
            "results": [match[0] for match in fuzzy_matches[:5]],
            "search_strategy": "fuzzy_name_match",
            "total_matches": len(fuzzy_matches),
            "explanation": f"Found {len(fuzzy_matches)} similar color names for '{query}'"
        }
    
    # STRATEGY 4: Enhanced semantic analysis
    search_intent = parse_search_intent_enhanced(query)
    
    # Apply semantic matching
    matches = []
    for color in catalog:
        score = calculate_match_score(color, search_intent, criteria or {})
        if score > 0.15:  # Threshold for relevance
            matches.append({
                "color": color,
                "score": score,
                "match_reasons": explain_match(color, search_intent, score)
            })
    
    # Sort by score only (objective scoring)
    matches.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "results": [m["color"] for m in matches[:10]],
        "search_strategy": "semantic_analysis",
        "search_intent": search_intent,
        "total_matches": len(matches),
        "explanation": f"Found {len(matches)} colors matching '{query}' using semantic analysis",
        "top_scores": [round(m["score"], 2) for m in matches[:5]]  # Show top 5 scores for transparency
    }


def parse_search_intent_enhanced(query: str) -> Dict[str, Any]:
    """
    Enhanced natural language parsing with better synonym recognition
    and contextual understanding.
    
    This provides a more sophisticated mapping from natural language
    to search parameters, while still being deterministic and fast.
    """
    query_lower = query.lower()
    
    # Room detection with synonyms
    rooms = []
    room_keywords = {
        "kitchen": ["kitchen", "cook", "culinary", "chef", "breakfast nook"],
        "living_room": ["living", "family room", "great room", "sitting room", "lounge", "den"],
        "bedroom": ["bedroom", "master", "sleep", "nursery", "guest room"],
        "bathroom": ["bathroom", "bath", "powder room", "washroom", "ensuite", "toilet"],
        "dining_room": ["dining", "eat", "dining room", "breakfast room"],
        "hallway": ["hallway", "corridor", "entry", "entryway", "foyer", "passage"],
        "exterior": ["exterior", "outside", "front door", "porch", "outdoor", "facade"],
        "office": ["office", "study", "workspace", "home office", "library"],
    }
    
    for room, keywords in room_keywords.items():
        if any(kw in query_lower for kw in keywords):
            rooms.append(room)
    
    # Color family detection with expanded vocabulary
    color_families = []
    color_keywords = {
        "white": ["white", "cream", "ivory", "off-white", "eggshell", "alabaster"],
        "gray": ["gray", "grey", "greige", "charcoal", "slate", "pewter", "taupe"],
        "beige": ["beige", "tan", "neutral", "sand", "khaki", "buff", "ecru"],
        "blue": ["blue", "navy", "teal", "turquoise", "cerulean", "indigo", "cobalt", "azure"],
        "green": ["green", "sage", "olive", "emerald", "forest", "mint", "seafoam", "lime"],
        "pink": ["pink", "rose", "blush", "coral", "salmon", "mauve", "magenta"],
        "red": ["red", "burgundy", "crimson", "scarlet", "maroon", "wine"],
        "yellow": ["yellow", "gold", "mustard", "ochre", "honey", "butter"],
        "brown": ["brown", "chocolate", "coffee", "cocoa", "mahogany", "chestnut"],
        "black": ["black", "charcoal black", "ebony", "jet"],
        "purple": ["purple", "violet", "lavender", "plum", "lilac", "aubergine"],
    }
    
    for family, keywords in color_keywords.items():
        if any(kw in query_lower for kw in keywords):
            color_families.append(family)
    
    # Undertone detection with enhanced vocabulary
    undertones = []
    
    # Warm undertone indicators
    warm_indicators = [
        "warm", "cozy", "inviting", "honey", "golden", "yellow-based",
        "yellow undertone", "peachy", "orange", "amber", "terracotta"
    ]
    if any(indicator in query_lower for indicator in warm_indicators):
        undertones.append("warm")
    
    # Cool undertone indicators
    cool_indicators = [
        "cool", "crisp", "fresh", "icy", "blue-based", "blue undertone",
        "steel", "arctic", "silvery", "frosty"
    ]
    if any(indicator in query_lower for indicator in cool_indicators):
        undertones.append("cool")
    
    # Neutral undertone indicators
    neutral_indicators = [
        "neutral", "balanced", "neither warm nor cool", "versatile",
        "true gray", "true white", "pure"
    ]
    if any(indicator in query_lower for indicator in neutral_indicators):
        undertones.append("neutral")
    
    # Brightness/intensity descriptors
    brightness_descriptors = []
    
    if any(word in query_lower for word in ["light", "bright", "pale", "soft", "airy", "luminous"]):
        brightness_descriptors.append("light")
    if any(word in query_lower for word in ["dark", "deep", "rich", "intense", "bold", "dramatic"]):
        brightness_descriptors.append("dark")
    if any(word in query_lower for word in ["medium", "mid-tone", "moderate"]):
        brightness_descriptors.append("medium")
    if any(word in query_lower for word in ["muted", "subtle", "understated", "quiet"]):
        brightness_descriptors.append("muted")
    if any(word in query_lower for word in ["vibrant", "saturated", "vivid", "strong"]):
        brightness_descriptors.append("vibrant")
    
    # Usage intent
    usage = []
    if any(word in query_lower for word in ["trim", "molding", "ceiling", "woodwork", "baseboard"]):
        usage.append("trim")
    if any(word in query_lower for word in ["wall", "walls", "paint", "painted"]):
        usage.append("walls")
    if any(word in query_lower for word in ["cabinet", "cabinets", "furniture", "built-in"]):
        usage.append("cabinets")
    if any(word in query_lower for word in ["door", "doors", "front door"]):
        usage.append("door")
    if any(word in query_lower for word in ["accent", "feature", "statement"]):
        usage.append("accent")
    
    # Style/mood descriptors
    mood = []
    if any(word in query_lower for word in ["modern", "contemporary", "minimalist", "clean"]):
        mood.append("modern")
    if any(word in query_lower for word in ["traditional", "classic", "timeless", "elegant"]):
        mood.append("traditional")
    if any(word in query_lower for word in ["cozy", "warm", "inviting", "comfortable"]):
        mood.append("cozy")
    if any(word in query_lower for word in ["dramatic", "bold", "statement", "striking"]):
        mood.append("dramatic")
    if any(word in query_lower for word in ["calming", "peaceful", "serene", "relaxing", "spa"]):
        mood.append("calming")
    if any(word in query_lower for word in ["sophisticated", "refined", "upscale", "luxurious"]):
        mood.append("sophisticated")
    
    # Exclusion detection (important for "NOT like X" queries)
    exclusions = []
    exclusion_patterns = [
        "not like", "nothing like", "different from", "don't want",
        "avoid", "except", "but not", "anything but"
    ]
    
    has_exclusion = any(pattern in query_lower for pattern in exclusion_patterns)
    if has_exclusion:
        # Try to extract what they want to exclude
        # This is a simple heuristic - in practice the LLM agent should handle this
        exclusions.append("user_specified_exclusion_detected")
    
    return {
        "rooms": rooms,
        "color_families": color_families,
        "undertones": undertones,
        "brightness_descriptors": brightness_descriptors,
        "usage": usage,
        "mood": mood,
        "exclusions": exclusions,
        "original_query": query
    }


# Backward compatibility alias
def parse_search_intent(query: str) -> Dict[str, Any]:
    """
    Backward compatibility wrapper for parse_search_intent_enhanced.
    Maintains the old function name for existing code.
    """
    return parse_search_intent_enhanced(query)

