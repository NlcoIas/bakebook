# M5 Issues

## 1. FastAPI Query `regex` deprecated
**Problem**: `Query("all", regex="...")` emits deprecation warning.
**Fix**: Changed to `pattern="..."`.

## 2. Insights summary loads all ingredients eagerly
**Problem**: The flour-kg and cost calculation in the summary endpoint loads recipe ingredients for every bake, which could be slow with many bakes.
**Impact**: Fine for personal use (<100 bakes). Would need optimization for scale.
