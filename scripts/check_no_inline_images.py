#!/usr/bin/env python3
"""Pre-commit guard: reject staged JSON files containing inline_data.data with non-empty bytes.

Usage (manual):   python scripts/check_no_inline_images.py
Pre-commit hook:  ln -sf ../../scripts/check_no_inline_images.py .git/hooks/pre-commit
                  (or wire it into pre-commit framework)
"""
import json
import subprocess
import sys
from pathlib import Path

THRESHOLD = 256  # base64 chars; tiny placeholders allowed


def staged_json_files():
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True, text=True, check=True,
    ).stdout.splitlines()
    return [Path(p) for p in out if p.endswith(".json") and Path(p).exists()]


def find_inline_data(node, path=""):
    hits = []
    if isinstance(node, dict):
        if "inline_data" in node and isinstance(node["inline_data"], dict):
            data = node["inline_data"].get("data", "")
            if isinstance(data, str) and len(data) > THRESHOLD:
                name = node["inline_data"].get("display_name", "?")
                hits.append((path, name, len(data)))
        for k, v in node.items():
            hits.extend(find_inline_data(v, f"{path}/{k}"))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            hits.extend(find_inline_data(v, f"{path}[{i}]"))
    return hits


def main():
    bad = []
    for f in staged_json_files():
        try:
            data = json.loads(f.read_text())
        except Exception:
            continue
        for hit in find_inline_data(data):
            bad.append((f, *hit))
    if bad:
        print("ERROR: staged JSON contains inline image data. Strip before committing:\n")
        for f, path, name, size in bad:
            print(f"  {f}  ->  {name}  ({size} b64 chars)  at {path}")
        print("\nFix: scripts/strip_inline_images.py <file>  (or remove the file)")
        sys.exit(1)


if __name__ == "__main__":
    main()
