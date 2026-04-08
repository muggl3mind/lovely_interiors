"""
Catalog utility functions.
Helper functions for catalog operations like brand normalization and name matching.
"""

from typing import Optional


def normalize_brand_code(brand_or_code: Optional[str]) -> str:
    """
    Normalize brand codes to standard format.
    
    Args:
        brand_or_code: Brand name or code to normalize
        
    Returns:
        Normalized brand code (BM, SW, FB, etc.)
    """
    if not brand_or_code:
        return ""
    
    s = str(brand_or_code).strip().lower()
    if s in {"bm", "benjamin moore"}:
        return "BM"
    if s in {"sw", "sherwin-williams", "sherwin williams"}:
        return "SW"
    if s in {"fb", "farrow & ball", "farrow and ball", "farrow-ball"}:
        return "FB"
    
    # Fallback to upper-cased token if looks like a short code
    return brand_or_code.strip().upper()


def is_similar_name(name1: str, name2: str) -> bool:
    """
    Check if two color names are similar (for typo detection).
    
    Args:
        name1: First color name
        name2: Second color name
        
    Returns:
        True if names are similar enough to be considered matches
    """
    # Skip if names are very different in length
    if abs(len(name1) - len(name2)) > 3:
        return False
    
    # Check if they share most characters (allowing for 1-2 typos)
    common_chars = sum(1 for c in name1 if c in name2)
    similarity = common_chars / max(len(name1), len(name2))
    
    # Also check word-level similarity for multi-word names
    words1 = name1.split()
    words2 = name2.split()
    if len(words1) > 1 and len(words2) > 1:
        word_matches = sum(1 for w1 in words1 if any(w1 in w2 or w2 in w1 for w2 in words2))
        word_similarity = word_matches / max(len(words1), len(words2))
        return similarity > 0.7 or word_similarity > 0.6
    
    return similarity > 0.8 