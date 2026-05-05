# M3 Issues

## 1. Schedule service naming mismatch
**Problem**: Route imported `StepInput` and `compute_ready_by` but agent created `ScheduleStep` and `calculate_schedule`.
**Fix**: Updated imports to match actual service exports.

## 2. Ready-by API failed silently in frontend
**Problem**: The API endpoint returned 500 because of the import error, but the ReadyByPanel just showed no data (no error displayed).
**Impact**: Fixed by correcting the import. Could add error state to the panel later.
