from typing import Dict, List, Any
import re


class RequirementTracker:
    """
    Tracks user requirements throughout the conversation to prevent drift
    and ensure recommendations stay aligned with original goals.
    """
    
    def __init__(self):
        self.requirements = {}
        self.original_vision = ""
        self.style_keywords = []
        self.color_preferences = []
        self.must_avoid = []
        self.rooms = []
        self.lighting_info = {}
    
    def set_initial_requirements(self, user_input: str) -> Dict[str, Any]:
        """Parse and store the user's initial vision."""
        self.original_vision = user_input
        user_lower = user_input.lower()
        
        # Extract key style indicators
        style_indicators = {
            "earthy": ["earthy", "earth", "natural", "organic"],
            "cottage": ["cottage", "french", "italian", "cozy"],
            "elegant": ["elegant", "sophisticated", "classy", "class"],
            "airy": ["airy", "light", "bright", "open"],
            "warm": ["warm", "cozy", "inviting"],
            "victorian": ["victorian", "estate"],
            "transitional": ["transitional", "mixing", "old with new"]
        }
        
        for style, keywords in style_indicators.items():
            if any(keyword in user_lower for keyword in keywords):
                self.style_keywords.append(style)
        
        # Extract color preferences
        if "earthy tones" in user_lower:
            self.color_preferences.append("earthy_tones")
        if "warm" in user_lower and "cool" not in user_lower:
            self.color_preferences.append("warm")
        elif "cool" in user_lower and "warm" not in user_lower:
            self.color_preferences.append("cool")
        if "neutral" in user_lower:
            self.color_preferences.append("neutral")
        if "pop of color" in user_lower:
            self.color_preferences.append("accent_color")
        if "color drenched" in user_lower:
            self.color_preferences.append("color_drenched_room")
            
        # Extract dislikes/must avoid
        hate_patterns = [
            r"hate\s+([^,.]+)",
            r"don't like\s+([^,.]+)",
            r"avoid\s+([^,.]+)"
        ]
        
        for pattern in hate_patterns:
            matches = re.findall(pattern, user_lower)
            for match in matches:
                if "vibrant" in match or "tacky" in match or "strong" in match:
                    self.must_avoid.append("vibrant_colors")
                if "commercial" in match:
                    self.must_avoid.append("commercial_colors")
                if "boring" in match:
                    self.must_avoid.append("boring_colors")
        
        # Extract rooms
        room_keywords = ["living room", "kitchen", "dining room", "hallway", "bedroom", "bathroom"]
        for room in room_keywords:
            if room in user_lower:
                self.rooms.append(room)
        
        # Extract lighting information
        if "north" in user_lower:
            self.lighting_info["north_facing"] = True
        if "south" in user_lower:
            self.lighting_info["south_facing"] = True
            
        return {
            "style_keywords": self.style_keywords,
            "color_preferences": self.color_preferences,
            "must_avoid": self.must_avoid,
            "rooms": self.rooms,
            "lighting_info": self.lighting_info
        }
    
    def validate_recommendation(self, color_name: str, description: str, room: str) -> Dict[str, Any]:
        """
        Check if a color recommendation aligns with original requirements.
        Returns validation results and suggestions for improvement.
        """
        issues = []
        alignment_score = 0
        description_lower = description.lower()
        
        # Check against style requirements
        if "earthy" in self.style_keywords:
            if any(word in description_lower for word in ["green", "brown", "beige", "stone", "natural", "earth"]):
                alignment_score += 3
            elif any(word in description_lower for word in ["charcoal", "dark grey", "dark gray", "black"]):
                issues.append(f"'{color_name}' (dark/charcoal) doesn't align with 'earthy' style preference")
        
        if "cottage" in self.style_keywords:
            if any(word in description_lower for word in ["soft", "muted", "gentle", "warm", "historic"]):
                alignment_score += 2
            elif any(word in description_lower for word in ["dramatic", "bold", "stark", "modern"]):
                issues.append(f"'{color_name}' described as dramatic/bold doesn't align with cottage style")
        
        if "elegant" in self.style_keywords:
            if any(word in description_lower for word in ["sophisticated", "timeless", "classic", "refined"]):
                alignment_score += 2
            elif any(word in description_lower for word in ["casual", "rustic", "rough"]):
                issues.append(f"'{color_name}' may be too casual for elegant aesthetic")
        
        if "airy" in self.style_keywords:
            if any(word in description_lower for word in ["light", "bright", "airy", "open"]):
                alignment_score += 2
            elif any(word in description_lower for word in ["dark", "deep", "heavy", "enveloping"]):
                issues.append(f"'{color_name}' described as dark/heavy conflicts with 'airy' requirement")
        
        # Check against color preferences
        if "earthy_tones" in self.color_preferences:
            if not any(word in description_lower for word in ["green", "brown", "beige", "stone", "earth", "natural", "grey", "gray"]):
                issues.append(f"'{color_name}' doesn't appear to be an earthy tone as requested")
        
        if "warm" in self.color_preferences:
            if any(word in description_lower for word in ["cool", "cold", "blue undertone", "grey undertone"]):
                issues.append(f"'{color_name}' appears cool-toned but user prefers warm colors")
        
        # Check against dislikes
        if "vibrant_colors" in self.must_avoid:
            if any(word in description_lower for word in ["vibrant", "bright", "bold", "saturated", "strong"]):
                issues.append(f"'{color_name}' may be too vibrant - user specifically dislikes vibrant/tacky colors")
        
        if "commercial_colors" in self.must_avoid:
            if any(word in description_lower for word in ["commercial", "standard", "basic"]):
                issues.append(f"'{color_name}' may feel too commercial for user's sophisticated taste")
        
        return {
            "alignment_score": alignment_score,
            "issues": issues,
            "passes_requirements": len(issues) == 0 and alignment_score > 0
        }
    
    def get_requirement_summary(self) -> str:
        """Return a summary of requirements for the agent to reference."""
        summary = f"ORIGINAL VISION: {self.original_vision[:200]}{'...' if len(self.original_vision) > 200 else ''}\n\n"
        summary += f"STYLE KEYWORDS: {', '.join(self.style_keywords)}\n"
        summary += f"COLOR PREFERENCES: {', '.join(self.color_preferences)}\n"
        summary += f"MUST AVOID: {', '.join(self.must_avoid)}\n"
        summary += f"ROOMS: {', '.join(self.rooms)}\n"
        return summary
    
    def check_recommendation_drift(self, proposed_colors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check if a set of color recommendations has drifted from original vision.
        Returns overall alignment assessment.
        """
        total_issues = []
        total_score = 0
        color_count = 0
        
        for color_info in proposed_colors:
            if "name" in color_info and "description" in color_info:
                validation = self.validate_recommendation(
                    color_info["name"],
                    color_info["description"],
                    color_info.get("room", "Unknown")
                )
                total_issues.extend(validation["issues"])
                total_score += validation["alignment_score"]
                color_count += 1
        
        avg_score = total_score / max(color_count, 1)
        
        return {
            "overall_alignment": "good" if avg_score >= 2 and len(total_issues) == 0 else 
                               "moderate" if avg_score >= 1 or len(total_issues) <= 2 else "poor",
            "alignment_score": avg_score,
            "total_issues": total_issues,
            "requires_course_correction": len(total_issues) > 2 or avg_score < 1
        }


def validate_schedule_with_requirements(
    schedule: Dict[str, Any], 
    requirements_tracker: RequirementTracker = None
) -> Dict[str, Any]:
    """
    Comprehensive validation that checks both catalog existence 
    and alignment with user requirements.
    """
    from .tools import validate_schedule
    
    # First do standard catalog validation
    catalog_validation = validate_schedule(schedule)
    
    # Then check requirement alignment if tracker provided
    requirement_issues = []
    requirement_alignment = "unknown"
    
    if requirements_tracker:
        proposed_colors = []
        
        for room in schedule.get("rooms", []):
            for key in ("walls", "trim", "ceiling"):
                color_pick = room.get(key)
                if color_pick and color_pick.get("name"):
                    proposed_colors.append({
                        "name": color_pick["name"],
                        "description": color_pick.get("description", ""),
                        "room": room.get("name", "Room"),
                        "location": key
                    })
        
        drift_check = requirements_tracker.check_recommendation_drift(proposed_colors)
        requirement_alignment = drift_check["overall_alignment"]
        
        for issue in drift_check["total_issues"]:
            requirement_issues.append(issue)
    
    return {
        **catalog_validation,
        "requirement_issues": requirement_issues,
        "requirement_alignment": requirement_alignment,
        "requirements_summary": requirements_tracker.get_requirement_summary() if requirements_tracker else "No requirements tracked"
    }


# Global tracker instance for the agent
_global_tracker = None

def track_requirements(user_input: str) -> dict:
    """
    Track user requirements from input text.
    Used by the agent to initialize or update requirement tracking.
    """
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = RequirementTracker()
    
    return _global_tracker.set_initial_requirements(user_input)

def validate_against_requirements(color_name: str, description: str, room: str = "Room") -> dict:
    """
    Validate a color recommendation against tracked requirements.
    Used by the agent to check if recommendations align with user goals.
    """
    global _global_tracker
    if _global_tracker is None:
        return {
            "error": "No requirements have been tracked yet. Call track_requirements first.",
            "passes_requirements": False
        }
    
    return _global_tracker.validate_recommendation(color_name, description, room)

def get_requirements_summary() -> str:
    """
    Get a summary of currently tracked requirements.
    """
    global _global_tracker
    if _global_tracker is None:
        return "No requirements tracked yet."
    
    return _global_tracker.get_requirement_summary()

# Test the requirement tracker when run directly
if __name__ == "__main__":
    print("Testing RequirementTracker...")
    
    test_input = '''Living Room, Hallway, Dining Room and Kitchen. Transitional with that french/italian cottage vibes. Cozy and airy but shows my personality. I love earthy tones and hate strong and vibrant tacky colors.'''
    
    tracker = RequirementTracker()
    requirements = tracker.set_initial_requirements(test_input)
    
    print("✓ Requirement tracking works")
    print(f"Style keywords found: {requirements['style_keywords']}")
    print(f"Color preferences: {requirements['color_preferences']}")  
    print(f"Must avoid: {requirements['must_avoid']}")
    print()
    
    # Test validation of a problematic recommendation (Down Pipe for earthy cottage)
    validation = tracker.validate_recommendation(
        'Down Pipe',
        'Dark lead grey with blue undertones',
        'Living Room'
    )
    print("Testing Down Pipe against earthy cottage requirements:")
    print(f"Alignment score: {validation['alignment_score']}")
    print(f"Issues found: {validation['issues']}")
    print(f"Passes requirements: {validation['passes_requirements']}")
    print()
    
    # Test validation of a good recommendation (Elephant's Breath for earthy cottage)
    validation2 = tracker.validate_recommendation(
        "Elephant's Breath",
        'Warm grey with magenta undertones, natural stone-like color',
        'Living Room'
    )
    print("Testing Elephant's Breath against earthy cottage requirements:")
    print(f"Alignment score: {validation2['alignment_score']}")
    print(f"Issues found: {validation2['issues']}")
    print(f"Passes requirements: {validation2['passes_requirements']}")
    
    print()
    print("✓ All requirement tracking working correctly!") 