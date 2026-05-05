#!/usr/bin/env python3
"""Validate and summarize the nutrition table.

The nutrition.json is hand-curated from USDA FoodData Central data.
This script validates the structure and prints a summary.
Run once; output is committed as data/nutrition.json.
"""

import json
import sys
from pathlib import Path

REQUIRED_FIELDS = {"kcal", "protein", "fat", "carbs", "sugar", "fiber", "salt"}

data_path = Path(__file__).parent.parent / "data" / "nutrition.json"

with open(data_path) as f:
    data = json.load(f)

errors = []
count = 0

for key, entry in data.items():
    if key.startswith("_"):
        continue
    count += 1
    if not isinstance(entry, dict):
        errors.append(f"{key}: not a dict")
        continue
    missing = REQUIRED_FIELDS - set(entry.keys())
    if missing:
        errors.append(f"{key}: missing fields {missing}")
    for field in REQUIRED_FIELDS:
        val = entry.get(field)
        if val is not None and not isinstance(val, (int, float)):
            errors.append(f"{key}.{field}: not a number ({type(val).__name__})")

if errors:
    print("Validation FAILED:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print(f"nutrition.json: {count} ingredients, all valid.")
print(f"Fields per entry: {', '.join(sorted(REQUIRED_FIELDS))}")
