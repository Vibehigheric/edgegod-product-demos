"""Validate tracked synthetic fixtures and run every offline demo check."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
files = subprocess.check_output(
    ["git", "ls-files", "-z"], cwd=ROOT
).decode().split("\0")
checks = []
json_count = 0
for name in filter(None, files):
    path = ROOT / name
    if path.suffix == ".json":
        json.loads(path.read_text(encoding="utf-8-sig"))
        json_count += 1
    if path.name == "check_demo.py":
        checks.append(path)
if not checks:
    raise SystemExit("No offline demo checks found")
for path in sorted(checks):
    subprocess.run([sys.executable, str(path)], cwd=path.parent, check=True)
print(f"PASS: {json_count} JSON files and {len(checks)} offline demo checks")
