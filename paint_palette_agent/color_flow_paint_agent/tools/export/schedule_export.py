"""
Schedule export functionality.
Exports validated paint schedules to downloadable text files.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
from ..validation.schedule_validator import validate_schedule

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = DATA_DIR / "output"


def export_schedule(schedule: Dict[str, Any]) -> Dict[str, Any]:
    """
    Export a plain-text schedule to data/output/schedule.txt and return its path.

    Expected schedule format (example):
    {
      "rooms": [
        {
          "name": "Living Room",
          "walls": {"brand": "FB", "name": "Elephant's Breath", "sheen": "Estate Emulsion"},
          "trim": {"brand": "FB", "name": "Wimborne White", "sheen": "Estate Eggshell"},
          "ceiling": {"brand": "FB", "name": "Wimborne White", "sheen": "Estate Emulsion"},
          "alternate": {"brand": "FB", "name": "Cornforth White"}
        }
      ]
    }
    """
    # Strict validation before writing
    validation = validate_schedule(schedule)
    if not validation.get("ok"):
        return {"error": "Validation failed: unknown colors present.", **validation}

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "schedule.txt"

    def format_color(p: Optional[Dict[str, Any]]) -> str:
        if not p:
            return "-"
        parts = []
        brand = p.get("brand", "-")
        name = p.get("name", "-")
        sheen = p.get("sheen")
        parts.append(f"{brand} {name}")
        if sheen:
            parts.append(f"— {sheen}")
        return " ".join(parts)

    lines: List[str] = []
    for room in schedule.get("rooms", []):
        lines.append(room.get("name", "Room"))
        lines.append(f"  Walls: {format_color(room.get('walls'))}")
        lines.append(f"  Trim: {format_color(room.get('trim'))}")
        lines.append(f"  Ceiling: {format_color(room.get('ceiling'))}")
        alt = room.get("alternate")
        if alt:
            lines.append(f"  Alternate Walls: {format_color(alt)}")
        lines.append("")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).strip() + "\n")

    return {"path": str(out_path)} 