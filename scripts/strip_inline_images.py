#!/usr/bin/env python3
"""Strip inline_data.data from an ADK eval set JSON in-place.

Usage: python scripts/strip_inline_images.py path/to/file.evalset.json [...]
"""
import json
import sys
from pathlib import Path


def strip(path: Path) -> int:
    data = json.loads(path.read_text())
    removed = 0

    def walk(node):
        nonlocal removed
        if isinstance(node, dict):
            if "inline_data" in node and isinstance(node["inline_data"], dict):
                inline = node["inline_data"]
                payload = inline.get("data", "")
                if isinstance(payload, str) and len(payload) > 0:
                    removed += len(payload)
                    inline["data"] = ""
                    inline["_note"] = (
                        "Image data stripped for public repo. "
                        "Provide locally via file_uri or repopulate from samples/."
                    )
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(data)
    path.write_text(json.dumps(data, indent=2))
    return removed


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    for arg in sys.argv[1:]:
        p = Path(arg)
        n = strip(p)
        print(f"{p}: stripped {n // 1024} KB of base64")


if __name__ == "__main__":
    main()
