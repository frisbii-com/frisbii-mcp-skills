#!/usr/bin/env python3
"""Record a Confluence page ID in docs/confluence/pages.json.

Usage: python3 scripts/set_page_id.py <skill-name|overview|calendar> <page-id> [<skill> <id> ...]
"""
import json
import sys
from pathlib import Path

path = Path(__file__).resolve().parent.parent / "docs/confluence/pages.json"
meta = json.loads(path.read_text())
args = sys.argv[1:]
if not args or len(args) % 2:
    sys.exit(__doc__)
for name, pid in zip(args[::2], args[1::2]):
    target = meta[name] if name in ("overview", "calendar") else meta["skills"][name]
    target["page_id"] = pid
path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n")
