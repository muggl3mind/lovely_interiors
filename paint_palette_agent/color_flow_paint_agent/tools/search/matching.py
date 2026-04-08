"""
Color matching and scoring algorithms - REDESIGNED VERSION
Evidence-based approach prioritizing objective measurements over subjective storytelling.

REVISION NOTES:
- Previous algorithm weighted F&B descriptions at 45% (too high - mostly marketing)
- Previous algorithm weighted hex codes at 10% (too low - objective visual data)
- Previous algorithm weighted names at 5% (arbitrary marketing names)

NEW APPROACH:
- Prioritize objective, measurable color attributes (hex, LRV)
- Use descriptions only for extracting technical terms
- Eliminate name-based scoring
- All heuristics are clearly marked as such
"""

from typing import Any, Dict, List
import re
import math


def calculate_match_score(color: Dict[str, Any], intent: Dict[str, Any], criteria: Dict[str, Any]) -> float:
    """
    Redesigned scoring that prioritizes objective color data.
    
    Weight Distribution:
    - Hex Color Similarity: 35% (objective visual matching)
    - LRV Matching: 30% (objective brightness for lighting conditions)
    - Undertone Matching: 25% (semi-objective, prevents clashes)
    - Description Mining: 10% (extract technical terms only, ignore storytelling)
    - Name Matching: 0% (eliminated - names are arbitrary)
    
    Total: 100%
    """
    
    score = 0.0
    
    # Hex Color Similarity (35%)
    hex_score = score_hex_similarity(color.get("hex"), intent)
    score += hex_score * 0.35
    
    # LRV Matching (30%)
    lrv_score = score_lrv_match(color.get("lrv"), intent)
    score += lrv_score * 0.30
    
    # Undertone Matching (25%)
    undertone_score = score_undertone_match(color, intent)
    score += undertone_score * 0.25
    
    # Description Mining (10%) - extract technical terms only
    description_score = mine_technical_terms(color.get("description", ""), intent)
    score += description_score * 0.10
    
    # Name: 0% - eliminated
    
    return min(score, 1.0)


def score_hex_similarity(hex_code: str, intent: Dict[str, Any]) -> float:
    """
    Score based on objective hex color similarity.
    
    Uses RGB distance and perceptual color matching.
    """
    if not hex_code or len(hex_code) != 7:
        return 0.0
    
    try:
        r, g, b = int(hex_code[1:3], 16), int(hex_code[3:5], 16), int(hex_code[5:7], 16)
        score = 0.0
        
        # Color family matching (50% of hex score)
        # Based on RGB channel dominance
        color_families = intent.get("color_families", [])
        for family in color_families:
            if family == "white" and r > 240 and g > 240 and b > 240:
                score += 0.5
            elif family == "gray" and is_gray_rgb(r, g, b):
                score += 0.5
            elif family == "blue" and b > max(r, g) + 15:
                score += 0.5
            elif family == "green" and g > max(r, b) + 15:
                score += 0.5
            elif family == "red" and r > max(g, b) + 15:
                score += 0.5
            elif family == "yellow" and r > 200 and g > 200 and b < 150:
                score += 0.5
            elif family == "beige" and r > g > b and (r - b) < 50:
                score += 0.5
            elif family == "pink" and r > b > g and r > 180:
                score += 0.5
        
        # Temperature matching (30% of hex score)
        # Based on warm (red > blue) vs cool (blue > red)
        undertones = intent.get("undertones", [])
        for undertone in undertones:
            if undertone == "warm" and r > b + 15:
                score += 0.3
            elif undertone == "cool" and b > r + 15:
                score += 0.3
            elif undertone == "neutral" and abs(r - b) <= 15:
                score += 0.3
        
        # Brightness range matching (20% of hex score)
        # Match requested brightness ranges
        brightness = (r + g + b) / 3
        if "light" in intent.get("original_query", "").lower() and brightness > 200:
            score += 0.2
        elif "dark" in intent.get("original_query", "").lower() and brightness < 100:
            score += 0.2
        elif "medium" in intent.get("original_query", "").lower() and 100 <= brightness <= 200:
            score += 0.2
        
        return min(score, 1.0)
        
    except (ValueError, TypeError):
        return 0.0


def is_gray_rgb(r: int, g: int, b: int) -> bool:
    """Check if RGB values represent a gray (low color saturation)."""
    # Grays have all channels within ~20 points of each other
    # and not too bright (not white)
    return (abs(r - g) < 20 and abs(g - b) < 20 and abs(r - b) < 20 
            and not (r > 240 and g > 240 and b > 240))


def score_lrv_match(lrv: float, intent: Dict[str, Any]) -> float:
    """
    Score based on Light Reflectance Value matching.
    
    LRV Scale (industry standard):
    - 0-25: Very dark (absorbs most light)
    - 25-50: Medium to dark
    - 50-70: Medium
    - 70-85: Light
    - 85-100: Very light (reflects most light)
    
    Room Recommendations (HEURISTIC - based on common practice):
    These are general guidelines, not hard rules. Actual recommendations
    should consider specific lighting, room size, and client preference.
    """
    if lrv is None or lrv < 0 or lrv > 100:
        return 0.0
    
    score = 0.0
    rooms = intent.get("rooms", [])
    
    # Room-specific LRV preferences (HEURISTIC)
    # Note: These are common design practices, not absolute rules
    room_lrv_prefs = {
        "kitchen": (65, 85),        # Generally prefer light/bright (but not required)
        "bathroom": (65, 85),       # Generally prefer light/fresh (but not required)
        "bedroom": (45, 75),        # Wide range acceptable
        "dining_room": (30, 80),    # Very flexible, can go dramatic or light
        "living_room": (45, 75),    # Wide range acceptable
        "hallway": (55, 80),        # Generally prefer light for openness
        "exterior": (20, 60),       # Often darker/more saturated
    }
    
    for room in rooms:
        if room in room_lrv_prefs:
            min_lrv, max_lrv = room_lrv_prefs[room]
            
            # Perfect match: within preferred range
            if min_lrv <= lrv <= max_lrv:
                score += 0.8
            # Close match: within 10 points of range
            elif abs(lrv - min_lrv) <= 10 or abs(lrv - max_lrv) <= 10:
                score += 0.5
            # Acceptable: within 20 points of range
            elif abs(lrv - min_lrv) <= 20 or abs(lrv - max_lrv) <= 20:
                score += 0.3
    
    # If no room specified, check general brightness descriptors
    if not rooms:
        query = intent.get("original_query", "").lower()
        if "bright" in query or "light" in query:
            # Prefer LRV 70+
            if lrv >= 70:
                score += 0.8
            elif lrv >= 60:
                score += 0.5
        elif "dark" in query or "deep" in query:
            # Prefer LRV <40
            if lrv < 40:
                score += 0.8
            elif lrv < 50:
                score += 0.5
    
    return min(score, 1.0)


def score_undertone_match(color: Dict[str, Any], intent: Dict[str, Any]) -> float:
    """
    Score based on undertone compatibility.
    
    Undertone Principle (ESTABLISHED):
    Undertone harmony is critical for preventing color clashes.
    Mixing warm and cool undertones on the same sightline typically
    creates visual discord.
    
    This is an established design principle found in professional
    color theory education.
    """
    score = 0.0
    
    # Extract undertone data from color
    color_undertones = color.get("undertone_tags", [])
    hue_family = color.get("hue_family", "")
    
    # Extract intent undertones
    intent_undertones = intent.get("undertones", [])
    intent_families = intent.get("color_families", [])
    
    # Direct undertone matching (60% of undertone score)
    if color_undertones and intent_undertones:
        for undertone in intent_undertones:
            if undertone in color_undertones:
                score += 0.6
                break
    
    # Hue family matching (40% of undertone score)
    if hue_family and intent_families:
        for family in intent_families:
            if family == hue_family or family in hue_family:
                score += 0.4
                break
    
    return min(score, 1.0)


def mine_technical_terms(description: str, intent: Dict[str, Any]) -> float:
    """
    Mine technical terms from descriptions, IGNORE marketing storytelling.
    
    Extract only:
    - Color family mentions (blue, gray, green, etc.)
    - Undertone descriptors (warm, cool, neutral)
    - Technical characteristics (deep, soft, strong, muted)
    
    Ignore:
    - Historical stories
    - Room name dropping
    - Poetic language
    - Brand storytelling
    """
    if not description or len(description) < 10:
        return 0.0
    
    description_lower = description.lower()
    score = 0.0
    
    # Extract color family technical terms (40% of description score)
    color_families = intent.get("color_families", [])
    technical_color_words = {
        "white": ["white", "ivory"],
        "gray": ["gray", "grey", "greige"],
        "blue": ["blue", "navy", "cobalt"],
        "green": ["green", "sage", "olive"],
        "beige": ["beige", "tan", "sand"],
        "pink": ["pink", "blush"],
        "red": ["red", "crimson"],
        "yellow": ["yellow", "gold"],
        "brown": ["brown", "umber"],
    }
    
    for family in color_families:
        if family in technical_color_words:
            terms = technical_color_words[family]
            # Only count if term appears in first 100 characters (technical description)
            first_part = description_lower[:100]
            if any(term in first_part for term in terms):
                score += 0.4
                break
    
    # Extract undertone technical terms (40% of description score)
    undertones = intent.get("undertones", [])
    technical_undertone_words = {
        "warm": ["warm", "yellow-based", "honey", "golden"],
        "cool": ["cool", "blue-based", "crisp", "icy"],
        "neutral": ["neutral", "balanced", "neither warm nor cool"],
    }
    
    for undertone in undertones:
        if undertone in technical_undertone_words:
            terms = technical_undertone_words[undertone]
            if any(term in description_lower for term in terms):
                score += 0.4
                break
    
    # Extract intensity descriptors (20% of description score)
    intensity_words = ["deep", "dark", "strong", "bold", "soft", "light", "pale", "muted", "vibrant"]
    query = intent.get("original_query", "").lower()
    
    for word in intensity_words:
        if word in query and word in description_lower[:100]:
            score += 0.2
            break
    
    return min(score, 1.0)


def explain_match(color: Dict[str, Any], intent: Dict[str, Any], score: float) -> List[str]:
    """Generate objective explanations for why this color matches."""
    reasons = []
    
    # LRV explanation
    lrv = color.get("lrv")
    if lrv:
        if lrv >= 70:
            reasons.append(f"Light & bright (LRV {lrv:.0f})")
        elif lrv >= 50:
            reasons.append(f"Medium brightness (LRV {lrv:.0f})")
        else:
            reasons.append(f"Rich & deep (LRV {lrv:.0f})")
    
    # Hex/visual explanation
    hex_code = color.get("hex")
    if hex_code:
        try:
            r, g, b = int(hex_code[1:3], 16), int(hex_code[3:5], 16), int(hex_code[5:7], 16)
            if b > r + 15:
                reasons.append("Cool-toned (blue-leaning)")
            elif r > b + 15:
                reasons.append("Warm-toned (red-leaning)")
            else:
                reasons.append("Neutral-toned (balanced)")
        except:
            pass
    
    # Undertone explanation
    undertones = color.get("undertone_tags", [])
    if undertones:
        reasons.append(f"Undertones: {', '.join(undertones)}")
    
    # Match quality
    if score >= 0.7:
        reasons.append("Strong match")
    elif score >= 0.5:
        reasons.append("Good match")
    
    return reasons


def calculate_universal_adjustments(color: Dict[str, Any], intent: Dict[str, Any]) -> float:
    """
    Universal adjustments (minor).
    
    Slight preference for colors with complete data,
    as they can be matched more accurately.
    """
    score = 0.0
    
    # Data completeness (modest boost)
    completeness = 0
    if color.get("hex"): completeness += 1
    if color.get("lrv") is not None: completeness += 1
    if color.get("undertone_tags"): completeness += 1
    if color.get("description"): completeness += 1
    
    # Max 0.2 boost for complete data (20% of universal adjustments)
    score += (completeness / 4) * 0.2
    
    return min(score, 1.0)


# Backward compatibility - keep old function names but redirect to new logic
def analyze_hex_color(hex_code: str, intent: Dict[str, Any]) -> float:
    """Backward compatibility wrapper."""
    return score_hex_similarity(hex_code, intent)


def analyze_lrv(lrv: float, hex_code: str, intent: Dict[str, Any]) -> float:
    """Backward compatibility wrapper."""
    return score_lrv_match(lrv, intent)


def analyze_undertones(color: Dict[str, Any], intent: Dict[str, Any]) -> float:
    """Backward compatibility wrapper."""
    return score_undertone_match(color, intent)


def analyze_description(description: str, intent: Dict[str, Any]) -> float:
    """Backward compatibility wrapper."""
    return mine_technical_terms(description, intent)

