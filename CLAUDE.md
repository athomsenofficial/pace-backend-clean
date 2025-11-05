# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **PACE (Promotion and Career Eligibility) System** - a full-stack application for processing Air Force promotion rosters, validating eligibility, and generating Master Eligibility Lists (MELs) as compliant PDF documents.

**Architecture:**
- **Backend:** FastAPI + Redis session management in `pace-backend-clean/`
- **Frontend:** React 19 + TypeScript + Vite in `pace-frontend-modern/`
- **Deployment:** Docker Compose backend on VPS (89.116.187.76), frontend can run locally or on hosting

## Development Commands

### Backend (pace-backend-clean)

#### Local Development
```bash
cd pace-backend-clean
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Running Backend Locally
```bash
# Ensure Redis is available (Docker or local)
docker-compose up redis -d

# Run FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Docker Development/Production
```bash
cd pace-backend-clean

# Build and run both backend + Redis
docker-compose up -d --build

# View logs
docker-compose logs -f backend

# Check container status
docker-compose ps

# Restart services
docker-compose down && docker-compose up -d --build

# Test health endpoint
curl http://localhost:8000/api/health
```

#### Debugging & Logs
- Session logs stored in `logs/` directory with format: `session_{session_id}_{cycle}_{year}.log`
- Docker logs: `docker-compose logs backend`
- Health check: `GET /api/health` returns `{"status": "healthy", "service": "pace-backend"}`

### Frontend (pace-frontend-modern)

```bash
cd pace-frontend-modern

# Install dependencies
npm install

# Development server (runs on port 5173)
npm run dev

# Production build
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

### VPS Deployment (Production)

**Server:** 89.116.187.76 (ssh root@89.116.187.76)

#### Deploy Backend to VPS
```bash
# Connect to VPS
ssh root@89.116.187.76

# Navigate to project
cd ~/pace-backend-clean

# Pull latest changes
git pull origin main

# Restart containers
docker-compose down
docker-compose up -d --build

# Verify deployment
docker-compose ps
curl http://localhost:8000/api/health
```

#### Production URL
- **API Base:** https://api.businessbydrew.cloud
- **Health Check:** https://api.businessbydrew.cloud/api/health

## Code Architecture

### Backend Core Processing Pipeline

The backend implements a multi-stage roster processing pipeline:

1. **File Upload & Validation** (`main.py`)
   - Accepts CSV/XLSX roster uploads via `/api/upload/{initial|final}-mel`
   - Validates file type, cycle (SRA/SSG/TSG/MSG/SMS), and year (2020-2030)
   - Creates Redis session with UUID and stores raw data

2. **Roster Processing** (`roster_processor.py`)
   - Validates required/optional columns against `constants.py` definitions
   - Parses dates using `date_parsing.py` (handles Excel serial dates + string formats)
   - Filters out officer ranks, enforces grade consistency
   - Computes accounting dates (120-day window before SCOD)
   - Calls `board_filter.py` for each member to determine eligibility

3. **Eligibility Logic** (`board_filter.py`)
   - Implements Air Force promotion eligibility rules:
     - **Time in Grade (TIG):** Checks date of rank meets minimum months for cycle
     - **Time in Service (TAFMSD):** Validates service dates
     - **High Year of Tenure (HYT):** Enforces separation windows (includes 2023-2026 exceptions)
     - **AFSC Skill Level:** Verifies primary/alternate AFSC meet grade requirements
     - **UIF Disposition:** Checks unfavorable information file closure timing
     - **Reenlistment Codes:** Validates RE status codes
     - **BTZ (Below-the-Zone):** A1C promotion eligibility for SRA cycle
   - Returns: `eligible`, `ineligible + reason`, `discrepancy` (manual review), or `BTZ-eligible`

4. **Small Unit Detection** (`roster_processor.py`)
   - Groups members by PAS code (unit identifier)
   - Flags units with ≤10 eligible members as "small units"
   - Small units for MSG/SMS automatically get consolidated senior rater
   - Stores PAS-to-unit-name mappings for senior rater forms

5. **Session Management** (`session_manager.py`)
   - Stores processed DataFrames as JSON lists in Redis
   - TTL: 1800 seconds (30 minutes)
   - Session contains: `eligible_df`, `ineligible_df`, `discrepancy_df`, `btz_df`, `small_unit_df`, `pascodes`, `pascode_unit_map`
   - PDF bytes cached after generation for download endpoints

6. **Senior Rater Collection** (frontend → backend)
   - Frontend collects SRID, name, rank, title per PAS code
   - `POST /api/{initial|final}-mel/submit/pascode-info` receives mapping
   - Backend expands session with senior rater data

7. **PDF Generation**
   - **Initial MEL** (`initial_mel_generator.py`):
     - Creates CUI-marked documents with unit logo, accounting dates
     - Sections: Eligible, Ineligible (with reasons), Discrepancy, BTZ
     - Computes MP/PN quotas using `promotion_eligible_counter.py`
     - Merges per-PAS PDFs into single downloadable file
   - **Final MEL** (`final_mel_generator.py`):
     - Interactive PDF with checkbox widgets (NRN/P/MP/PN) via PyMuPDF
     - Includes discrepancy pages for manual adjudication
     - Small unit packets generated separately
   - **PDF Templates** (`pdf_templates.py`):
     - Shared header/footer rendering with ReportLab
     - CUI marking, unit data blocks, compliance footers

### Frontend Architecture

**React Router Structure:**
- `src/App.tsx`: Main routing component
- `src/pages/`: Page components (InitialMEL, FinalMEL, Dashboard, HowTo, etc.)
- `src/features/mel/`: MEL-specific feature components
  - `FileUpload.tsx`: Drag-and-drop roster upload
  - `PascodeForm.tsx`: Senior rater data entry form
  - `RosterPreview.tsx`: Post-upload roster review interface
  - `EditMemberModal.tsx`, `AddMemberModal.tsx`, `DeleteConfirmDialog.tsx`: Roster editing
  - `LogoUploadModal.tsx`: Custom unit logo upload

**State Management:**
- React Query (`@tanstack/react-query`) for API calls
- Zustand for client state (if present)
- Supabase client in `src/lib/supabase.ts` for auth/database (future feature)

**Component Library:**
- Custom UI components in `src/shared/components/ui/`:
  - `Button.tsx`, `Input.tsx`, `Select.tsx`, `Card.tsx`, `Modal.tsx`, `Badge.tsx`, `Table.tsx`, `Tabs.tsx`
- Tailwind CSS with custom color palette (Electric Indigo primary, Cyber Teal success)

**API Integration:**
- Axios for HTTP requests
- Backend URL configured via `VITE_API_URL` environment variable
- Endpoints defined in API_REFERENCE.md

### Key Business Logic Files

- **`board_filter.py`**: Core eligibility determination (TIG, TAFMSD, HYT, AFSC, UIF, RE codes)
- **`accounting_date_check.py`**: 120-day PAS stability window validation
- **`constants.py`**: Centralized configuration:
  - `SCODS`: Promotion selection cutoff dates per cycle
  - `TIG_MONTHS_REQUIRED`: Minimum time in grade map
  - `GRADE_MAP`, `PROMOTIONAL_MAP`: Grade hierarchies
  - `PAFSC_MAP`: AFSC skill level requirements per grade
  - `RE_CODES`: Reenlistment code explanations
  - `OFFICER_RANKS`, `ENLISTED_RANKS`: Rank categorization
  - `cors_origins`: Allowed frontend origins for CORS
  - Feature flags, validation rules, PDF layout constants

### Session Lifecycle

1. User uploads roster → `POST /api/upload/{initial|final}-mel`
2. Backend creates session, processes roster → returns `session_id`, `pascodes[]`, `errors[]`, `senior_rater_needed` flag
3. Frontend stores session_id, displays PAS codes if `senior_rater_needed`
4. User enters senior rater info → `POST /api/{initial|final}-mel/submit/pascode-info`
5. Backend generates PDF, caches in Redis → returns PDF as streaming response
6. Alternative: `GET /api/download/{initial|final}-mel/{session_id}` retrieves cached PDF
7. Session expires after 30 minutes (TTL) or explicit cleanup

### Roster Editing Workflow

After initial upload, users can preview and edit roster via:
- `GET /api/roster/preview/{session_id}?category=all&page=1&page_size=50`
- `PUT /api/roster/member/{session_id}/{member_id}` - Edit member
- `DELETE /api/roster/member/{session_id}/{member_id}?reason=...&hard_delete=false` - Soft/hard delete
- `POST /api/roster/member/{session_id}` - Add new member
- `POST /api/roster/reprocess/{session_id}` - Re-run eligibility checks with updated data

All edits trigger `rescan_and_update_pascodes()` to keep PAS code tracking synchronized.

## Environment Configuration

### Backend (.env)
```bash
REDIS_URL=redis://redis:6379  # Docker internal network
# No other env vars required - Redis connection string is primary config
```

### Frontend (.env)
```bash
# Supabase (future authentication/database features)
VITE_SUPABASE_URL=https://swvkaqrdhyoccwtzqabg.supabase.co
VITE_SUPABASE_ANON_KEY=<anon_key>

# Backend API
VITE_API_URL=http://localhost:8000           # Local dev
# VITE_API_URL=https://api.businessbydrew.cloud  # Production

# Environment
VITE_ENV=development
```

## Critical Implementation Notes

### CORS Configuration
- Backend CORS is explicitly allow-listed in `constants.py` → `cors_origins`
- Includes localhost ports (5173, 5174, 3000) + production domains
- **Never use wildcard `"*"` in production** - security risk for credential-based requests

### Date Parsing
- `date_parsing.py` handles both Excel serial dates and string formats
- Always use `parse_date()` utility - returns `datetime` objects or `None`
- Date columns: `DOR`, `UIF_DISPOSITION_DATE`, `TAFMSD`, `DATE_ARRIVED_STATION`
- Display format: `DD-MMM-YYYY` (e.g., `15-MAR-2024`)

### Grade Filtering
- Officers are filtered out early in processing (roster_processor.py)
- Only enlisted ranks (AB through CMSgt) are processed for promotion
- Grade validation uses `GRADE_MAP` and `PROMOTIONAL_MAP` from constants.py

### Small Unit Consolidation
- Threshold: ≤10 eligible members per PAS code
- MSG/SMS cycles: all units get consolidated senior rater by default
- Frontend renders separate senior rater inputs for small units
- PDF generation creates separate small-unit packets

### Session Persistence
- Redis stores JSON-serialized DataFrames as list[dict]
- PDF binaries stored as bytes in Redis key `pdf:{session_id}`
- All dates stored as ISO strings in Redis, parsed back to datetime on retrieval
- Soft-deleted members marked with `deleted: true` flag, retained for audit

### PDF Generation Dependencies
- ReportLab: Core PDF rendering (Initial MEL)
- PyMuPDF (fitz): Interactive form fields (Final MEL checkboxes)
- PyPDF2: PDF merging
- Fonts: Calibri TTF files in `pace-backend-clean/fonts/`
- Logos: Unit logos in `pace-backend-clean/images/`, default is `fiftyonefss.jpeg`

### Testing
- No pytest currently installed/configured in requirements.txt
- Manual testing via API endpoints and frontend workflows
- Health check endpoint (`/api/health`) for deployment verification

## Common Development Workflows

### Adding a New Eligibility Rule
1. Update business logic in `board_filter.py` (add new check function)
2. Modify `board_filter()` main function to call new check
3. Add any constants to `constants.py` (e.g., new SCOD dates, thresholds)
4. Update ineligibility reason string in return tuple
5. Test with sample roster data

### Changing PDF Layout
1. Modify `pdf_templates.py` for shared header/footer/section rendering
2. Update `initial_mel_generator.py` or `final_mel_generator.py` for specific MEL type
3. Adjust measurements (use `inch` unit from ReportLab)
4. Test PDF generation with real session data

### Adding a New API Endpoint
1. Define Pydantic model in `classes.py` if needed
2. Add FastAPI route in `main.py` with appropriate HTTP verb decorator
3. Use `get_session()` / `update_session()` for Redis operations
4. Return `JSONResponse` or `StreamingResponse` for PDFs
5. Update `cors_origins` if frontend domain changes
6. Document endpoint in API_REFERENCE.md

### Modifying Frontend UI
1. Locate page component in `src/pages/` or feature component in `src/features/`
2. Use existing UI components from `src/shared/components/ui/`
3. Follow Tailwind CSS class naming (primary = indigo, success = teal)
4. API calls should use axios with `VITE_API_URL` from env
5. Handle loading/error states explicitly

## Important File Locations

- **Eligibility Rules:** `pace-backend-clean/board_filter.py`
- **Business Constants:** `pace-backend-clean/constants.py`
- **API Routes:** `pace-backend-clean/main.py`
- **Session Logic:** `pace-backend-clean/session_manager.py`
- **PDF Templates:** `pace-backend-clean/pdf_templates.py`
- **Date Utilities:** `pace-backend-clean/date_parsing.py`
- **Frontend Routes:** `pace-frontend-modern/src/App.tsx`
- **MEL Upload Flow:** `pace-frontend-modern/src/pages/InitialMEL.tsx` and `FinalMEL.tsx`
- **API Client:** Frontend uses axios directly, no centralized API client file
- **UI Components:** `pace-frontend-modern/src/shared/components/ui/`

## Troubleshooting

### Backend won't start
- Check Redis is running: `docker-compose ps` or `redis-cli ping`
- Verify REDIS_URL in environment matches container network
- Check logs: `docker-compose logs backend`

### PDF generation fails
- Verify fonts exist in `pace-backend-clean/fonts/` (calibri.ttf, calibrib.ttf)
- Check logo files in `pace-backend-clean/images/`
- Ensure ReportLab/PyMuPDF/PyPDF2 installed: `pip list`
- Check session contains all required keys: eligible_df, pascode_info, etc.

### Frontend can't connect to backend
- Verify `VITE_API_URL` in `.env` matches backend URL
- Check CORS origins in `pace-backend-clean/constants.py` include frontend origin
- Test backend health: `curl http://localhost:8000/api/health`
- Check browser console for CORS errors

### Session not found errors
- Sessions expire after 30 minutes (1800s TTL)
- Check Redis is retaining data: `docker exec -it pace-redis redis-cli KEYS session:*`
- Verify session_id is being passed correctly in API calls

### Eligibility calculation incorrect
- Review business rules in `board_filter.py` against Air Force promotion policy
- Check SCOD dates in `constants.py` → `SCODS` dict
- Verify TIG requirements in `TIG_MONTHS_REQUIRED` dict
- Enable debug logging: update `logging_config.py` to DEBUG level
- Check session logs in `logs/` directory for member-by-member processing

## Production Deployment Notes

- Backend runs on VPS 89.116.187.76 via Docker Compose
- Nginx reverse proxy handles HTTPS (api.businessbydrew.cloud) → backend:8000
- Frontend deployment: Not currently deployed, can be hosted on Vercel/Netlify/VPS
- Redis data is ephemeral (no persistent volume in production) - sessions are temporary
- SSL certificates managed by Certbot (Let's Encrypt) on VPS
- Check HOSTINGER_SSH_COMMANDS.md and QUICK_RESTART_GUIDE.md for deployment procedures
