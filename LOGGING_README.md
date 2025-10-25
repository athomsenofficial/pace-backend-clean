# PACE Backend Logging System

## Overview

The PACE backend creates a **separate log file for each roster upload**. Every step of the eligibility determination process is logged to its own file, making it easy to track and review specific processing sessions.

## Log Files Location

All log files are stored in the `/logs` directory:

```
pace-backend-clean/
├── logs/
│   ├── SRA_2025_20251023_170542_abc123de.log   # Session-specific roster log
│   ├── SSG_2025_20251023_180234_def456gh.log   # Another session log
│   ├── TSG_2024_20251023_150123_ghi789jk.log   # Another session log
│   ├── uploads.log                              # Summary of all uploads
│   └── general.log                              # General application logs
```

### Log File Naming Convention

Session logs are named: `{CYCLE}_{YEAR}_{TIMESTAMP}_{SESSION_ID}.log`

- **CYCLE**: Promotion cycle (SRA, SSG, TSG, MSG, SMS)
- **YEAR**: Promotion year
- **TIMESTAMP**: When processing started (YYYYMMDD_HHMMSS)
- **SESSION_ID**: First 8 characters of the session ID

**Example**: `SRA_2025_20251023_170542_abc123de.log`
- SRA promotion cycle for 2025
- Started October 23, 2025 at 5:05:42 PM
- Session ID starts with "abc123de"

## Log File Contents

### Session Log Files (e.g., SRA_2025_20251023_170542_abc123de.log)

Each session log is a **complete, self-contained record** of an entire roster processing session. It contains:

1. **Session Header** - Cycle, year, session ID, start time, log filename
2. **Upload Summary** - Total members to process
3. **Member-by-Member Processing** - EVERY SINGLE MEMBER on the roster
4. **Processing Summary** - Final statistics
5. **Session Footer** - Completion status and end time

The session log contains detailed step-by-step processing for **EVERY SINGLE MEMBER** on the roster:

#### Initial Processing (for all members):
- ROW number and member identification (name, SSAN, grade)
- Promotion cycle information
- Projected grade status
- Early filter checks:
  - ❌ **Officer Rank Check** - Officers excluded from enlisted promotions
  - ❌ **Invalid Rank Check** - Unknown or unsupported ranks
  - ❌ **Already Projected** - Members already selected for promotion
  - ❌ **Wrong Cycle** - Grade doesn't match promotion cycle (e.g., SSG in TSG cycle)
  - ❌ **Missing Data** - Required data fields missing
  - ❌ **Accounting Date** - Failed date arrived station check
  - ✓ **Passed Early Filters** - Member continues to detailed board filter

#### Detailed Board Filter (only for members who pass early filters):
Each member gets 11-step detailed eligibility check:
- Step 1: Date parsing
- Step 2: Key dates calculation (SCOD, TIG, TIS, HYT, MDOS)
- Step 3: A1C eligibility checks
- Step 4: 3-year TIS check
- Step 5: Time in Grade (TIG) check
- Step 6: Time in Service (TIS) check
- Step 7: High Year of Tenure (HYT) check
- Step 8: UIF code check
- Step 9: RE status check
- Step 10: PAFSC skill level check
- Step 11: Final eligibility determination

#### Final Decision (all members get one):
- ✅ **ELIGIBLE** - Meets all requirements
- ✅ **ELIGIBLE (BTZ)** - Below-the-Zone eligible
- ✅ **ELIGIBLE (WITH DISCREPANCY)** - Eligible but flagged for review
- ❌ **INELIGIBLE** - Failed one or more checks (with reason)
- ❌ **EXCLUDED** - Filtered out before board filter (with reason)

**Key Point:** Every person on your roster will have an entry in this log explaining their status!

**Example 1 - Member Filtered Out Early (SSG projected for TSG):**
```
2025-10-23 16:30:46 | board_filter | INFO | ============================================================
2025-10-23 16:30:46 | board_filter | INFO | ROW 42: Processing WHITE, JOHN (SSAN: 5678)
2025-10-23 16:30:46 | board_filter | INFO |   Current Grade: SSG
2025-10-23 16:30:46 | board_filter | INFO |   Promotion Cycle: TSG 2025
2025-10-23 16:30:46 | board_filter | INFO |   Projected Grade: TSG
2025-10-23 16:30:46 | board_filter | INFO |   ❌ EXCLUDED: Projected for TSG (next grade)
2025-10-23 16:30:46 | board_filter | INFO |   Decision: Skipped (Projected for Next Grade)
```

**Example 2 - Member Who Passes All Checks:**
```
2025-10-23 16:30:46 | board_filter | INFO | ============================================================
2025-10-23 16:30:46 | board_filter | INFO | ROW 15: Processing SMITH, JOHN A (SSAN: 1234)
2025-10-23 16:30:46 | board_filter | INFO | Grade: SRA | Year: 2025
2025-10-23 16:30:46 | board_filter | INFO | Input Data - DOR: 01-JAN-2023, TAFMSD: 01-JAN-2020, UIF: 0
2025-10-23 16:30:46 | board_filter | INFO | Step 1: Parsing dates
2025-10-23 16:30:46 | board_filter | INFO |   Parsed DOR: 2023-01-01 00:00:00
2025-10-23 16:30:46 | board_filter | INFO |   Parsed TAFMSD: 2020-01-01 00:00:00
2025-10-23 16:30:46 | board_filter | INFO |   Parsed UIF Disposition: None
2025-10-23 16:30:46 | board_filter | INFO | Step 2: Calculating key dates and thresholds
2025-10-23 16:30:46 | board_filter | INFO |   SCOD (Selection Cutoff Date): 31-MAR-2025
2025-10-23 16:30:46 | board_filter | INFO |   TIG Eligibility Month: 01-SEP-2024 (requires 6 months TIG)
2025-10-23 16:30:46 | board_filter | INFO |   TAFMSD Required Date: 01-JUL-2023 (requires 3.0 years TIS)
2025-10-23 16:30:46 | board_filter | INFO |   HYT Date: 01-JAN-2028 (10 years)
2025-10-23 16:30:46 | board_filter | INFO |   MDOS (Mandatory Date of Separation): 31-MAY-2026
...
2025-10-23 16:30:46 | board_filter | INFO | Step 11: Final Eligibility Determination
2025-10-23 16:30:46 | board_filter | INFO |   ELIGIBLE: SMITH, JOHN A meets all requirements
2025-10-23 16:30:46 | board_filter | INFO | ============================================================
```

## How to Read the Logs

### 1. Finding Your Most Recent Session
List log files by date:
```bash
ls -lt logs/*.log | head -5
```

### 2. Opening a Specific Session Log
```bash
# Open the most recent SRA cycle log
open logs/SRA_2025_*.log

# Or use cat/less to view in terminal
cat logs/SRA_2025_20251023_170542_abc123de.log
less logs/SRA_2025_20251023_170542_abc123de.log
```

### 3. Finding a Specific Member in a Session Log
Search by member name or SSAN within a specific session file:
```bash
grep "WHITE, JOHN" logs/SRA_2025_20251023_170542_abc123de.log
grep "SSAN: 5678" logs/SRA_2025_20251023_170542_abc123de.log
```

### 4. Finding All Failures in a Session
```bash
grep "FAILED\|INELIGIBLE\|EXCLUDED" logs/SRA_2025_20251023_170542_abc123de.log
```

### 5. Viewing the Processing Summary
```bash
grep -A 10 "PROCESSING SUMMARY" logs/SRA_2025_20251023_170542_abc123de.log
```

### 6. Viewing Real-Time Logs (During Upload)
Watch the most recent log file as it's being written:
```bash
# Find and tail the newest log file
tail -f $(ls -t logs/*.log | head -1)
```

### 7. Finding Members Filtered Out by Specific Reasons

Replace `SESSION_FILE` with your actual session log filename:

**Already Projected for Next Grade:**
```bash
grep "Projected for Next Grade" logs/SESSION_FILE.log
```

**Wrong Cycle (grade doesn't match):**
```bash
grep "Wrong Cycle" logs/SESSION_FILE.log
```

**Officers Excluded:**
```bash
grep "Officer rank" logs/SESSION_FILE.log
```

**Missing Required Data:**
```bash
grep "Missing required" logs/SESSION_FILE.log
```

**Failed Accounting Date:**
```bash
grep "Accounting Date" logs/SESSION_FILE.log
```

## Understanding Eligibility Decisions

### ELIGIBLE
- Member passed all checks
- Will appear on eligible roster

### ELIGIBLE (BTZ)
- Member qualified for Below The Zone promotion
- Special A1C promotion category

### INELIGIBLE
- Member failed one or more checks
- Reason will be logged
- Common reasons:
  - Insufficient TIG (Time in Grade)
  - Insufficient TIS (Time in Service)
  - Higher tenure issues
  - Failed A1C check
  - 3-year TIS restriction

### DISCREPANCY
- Member has a flag that needs review
- Will appear on eligible roster with notation
- Common reasons:
  - UIF code > 1
  - RE status code issue
  - Insufficient PAFSC skill level

## Log Rotation and Management

### Per-Session Logs Benefits
- **Easy to find**: Each roster gets its own file
- **No mixing**: No confusion between different rosters
- **Easy to delete**: Remove old sessions without affecting recent ones
- **Easy to share**: Send specific session logs to others

### Manual Cleanup
Delete logs older than 30 days:
```bash
find logs/ -name "*.log" -type f -mtime +30 -delete
```

Archive old logs before deleting:
```bash
# Archive logs older than 30 days
find logs/ -name "*.log" -type f -mtime +30 -exec tar -czf logs_archive_$(date +%Y%m%d).tar.gz {} +

# Then delete them
find logs/ -name "*.log" -type f -mtime +30 -delete
```

Delete specific cycle logs:
```bash
# Delete all SSG 2024 logs
rm logs/SSG_2024_*.log
```

### View Log File Sizes
```bash
# List all log files with sizes
ls -lh logs/*.log

# Show disk usage by logs directory
du -h logs/
```

## Backup Location

All backend files have been backed up before logging implementation:
- Location: `/backups/`
- Format: `backup_YYYYMMDD_HHMMSS.tar.gz`
- Current backup: `backup_20251023_160659.tar.gz`

## Troubleshooting

### No logs appearing
1. Check if the `logs` directory exists
2. Verify file permissions
3. Check that the application is running

### Logs too large
1. Implement log rotation
2. Archive old logs
3. Consider filtering to ERROR level only for production

### Finding specific issues
Use grep with context:
```bash
# Show 5 lines before and after the error
grep -A 5 -B 5 "FAILED" logs/board_filter.log
```

## Log Levels

- **INFO**: Normal operation, informational messages
- **WARNING**: Issues that don't prevent processing (e.g., discrepancies)
- **ERROR**: Errors that prevent processing
- **EXCEPTION**: Critical errors with stack traces

## Quick Reference

### Finding SSG White's Status

```bash
# List recent SSG logs
ls -lt logs/SSG_*.log

# Search for White in the most recent SSG log
grep "WHITE" $(ls -t logs/SSG_*.log | head -1)
```

### Common Searches

```bash
# Find all eligible members in a session
grep "✅ ELIGIBLE" logs/SESSION_FILE.log

# Find all ineligible members in a session
grep "❌ INELIGIBLE" logs/SESSION_FILE.log

# Find all members excluded before board filter
grep "❌ EXCLUDED" logs/SESSION_FILE.log

# Get processing statistics
grep -A 10 "PROCESSING SUMMARY" logs/SESSION_FILE.log
```

## Questions?

Each roster upload creates its own complete log file. If you need to understand why a specific member was marked eligible or ineligible:

1. Find the session log for that roster (by date/cycle/year)
2. Search for the member's name or SSAN
3. Read through their processing steps to see the decision

Every person on your roster will have a complete audit trail in their session's log file!
