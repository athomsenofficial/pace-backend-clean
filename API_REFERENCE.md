# API Configuration Reference

## Environment Information

### Production API
- **Domain**: api.businessbydrew.cloud
- **URL**: https://api.businessbydrew.cloud
- **Server**: 89.116.187.76
- **Protocol**: HTTPS

### Supabase Configuration
- **URL**: https://swvkaqrdhyoccwtzqabg.supabase.co
- **Anon Key**: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN3dmthcXJkaHlvY2N3dHpxYWJnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE0ODIxMTYsImV4cCI6MjA3NzA1ODExNn0.hLQ8NN9npdpHCA3IWlvqWKZB1m0ASCs-omeSkU__XHs

### Local Development
- **Backend URL**: http://localhost:8000
- **Backend Port**: 8000
- **Frontend Ports**: 5173, 5174, 3000
- **Redis Port**: 6379

---

## Backend API Endpoints

### Health Check
- **GET** `/api/health`
  - Health check endpoint for Docker and load balancers
  - Returns: `{"status": "healthy", "service": "pace-backend"}`

### Initial MEL Operations

#### Upload Initial MEL
- **POST** `/api/upload/initial-mel`
  - Upload roster file for Initial MEL processing
  - Form Data:
    - `file`: CSV or Excel file
    - `cycle`: Promotion cycle (SRA, SSG, TSG, MSG, SMS)
    - `year`: Promotion year (2020-2030)
  - Returns: Session ID, pascodes, errors, senior_rater_needed flag

#### Download Initial MEL
- **GET** `/api/download/initial-mel/{session_id}`
  - Download generated Initial MEL PDF
  - Returns: PDF file

#### Submit Initial MEL Pascode Info
- **POST** `/api/initial-mel/submit/pascode-info`
  - Submit pascode information and generate PDF
  - Body: `{"session_id": string, "pascode_info": object}`
  - Returns: PDF file

### Final MEL Operations

#### Upload Final MEL
- **POST** `/api/upload/final-mel`
  - Upload roster file for Final MEL processing
  - Form Data:
    - `file`: CSV or Excel file
    - `cycle`: Promotion cycle (SRA, SSG, TSG, MSG, SMS)
    - `year`: Promotion year (2020-2030)
  - Returns: Session ID, pascodes, errors, senior_rater_needed flag

#### Download Final MEL
- **GET** `/api/download/final-mel/{session_id}`
  - Download generated Final MEL PDF
  - Returns: PDF file

#### Submit Final MEL Pascode Info
- **POST** `/api/final-mel/submit/pascode-info`
  - Submit pascode information and generate PDF
  - Body: `{"session_id": string, "pascode_info": object}`
  - Returns: PDF file

### Roster Management

#### Get Roster Preview
- **GET** `/api/roster/preview/{session_id}`
  - Get roster preview for review and editing
  - Query params:
    - `category`: Filter by category (default: "all")
    - `page`: Page number (default: 1)
    - `page_size`: Items per page (default: 50)
  - Returns: Full roster data with categories, statistics, errors

#### Edit Roster Member
- **PUT** `/api/roster/member/{session_id}/{member_id}`
  - Edit an existing member in the roster
  - Body: Member data object
  - Returns: Success message

#### Delete Roster Member
- **DELETE** `/api/roster/member/{session_id}/{member_id}`
  - Delete a member from the roster
  - Query params:
    - `reason`: Deletion reason (required)
    - `hard_delete`: Permanent deletion flag (default: false)
  - Returns: Success message

#### Add Roster Member
- **POST** `/api/roster/member/{session_id}`
  - Add a new member to the roster
  - Body:
    ```json
    {
      "category": "eligible|ineligible|discrepancy|btz|small_unit",
      "data": { member fields },
      "reason": "reason for adding",
      "run_eligibility_check": boolean
    }
    ```
  - Returns: Success message, member_id

#### Reprocess Roster
- **POST** `/api/roster/reprocess/{session_id}`
  - Reprocess the roster with updated eligibility rules
  - Body:
    ```json
    {
      "preserve_manual_edits": boolean,
      "categories": []
    }
    ```
  - Returns: Success message

### Logo Management

#### Upload Logo
- **POST** `/api/roster/logo/{session_id}`
  - Upload custom logo for roster
  - Form Data: `logo`: PNG or JPG file
  - Returns: Success message, filename

#### Get Logo
- **GET** `/api/roster/logo/{session_id}`
  - Get custom logo for roster
  - Returns: Image file

#### Delete Logo
- **DELETE** `/api/roster/logo/{session_id}`
  - Delete custom logo
  - Returns: Success message

---

## CORS Origins (Backend)

The backend accepts requests from:
- http://localhost:5173
- http://localhost:5174
- http://localhost:3000
- https://hammerhead-app-bqr7z.ondigitalocean.app
- https://api.pace-af-tool.com
- https://pace-af-tool.com
- https://www.api.pace-af-tool.com
- https://www.pace-af-tool.com

---

## Configuration Files

### Frontend Environment (.env)
```bash
# Supabase Configuration
VITE_SUPABASE_URL=https://swvkaqrdhyoccwtzqabg.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN3dmthcXJkaHlvY2N3dHpxYWJnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE0ODIxMTYsImV4cCI6MjA3NzA1ODExNn0.hLQ8NN9npdpHCA3IWlvqWKZB1m0ASCs-omeSkU__XHs

# Backend API Configuration
# Production:
# VITE_API_URL=https://api.businessbydrew.cloud

# Local Development:
VITE_API_URL=http://localhost:8000

# Environment
VITE_ENV=development
```

### Backend Constants (constants.py)
- CORS origins configured in `cors_origins` list
- Session TTL: 1800 seconds (30 minutes)
- Max file size: 50MB
- Allowed file types: CSV, XLSX

---

## Docker Configuration

### Backend (docker-compose.yml)
```yaml
services:
  redis:
    port: 6379
  backend:
    port: 8000
    environment:
      - REDIS_URL=redis://redis:6379
```

---

## SSH Access (Production Server)
- **Host**: 89.116.187.76
- **User**: root
- **Password**: .u4LJ4Pc?xQ,U;p7zAGX

---

## Notes
- Backend runs in Docker containers (backend + redis)
- Frontend uses Vite for development server
- API uses FastAPI with CORS middleware
- Session management via Redis
- PDF generation uses ReportLab
