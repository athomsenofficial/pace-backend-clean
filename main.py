import os
import io
import uuid
from fastapi import Body, FastAPI, Form, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
import pandas as pd
from final_mel_generator import generate_final_roster_pdf
from session_manager import create_session, get_pdf_from_redis, get_session, update_session, delete_session
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Optional
from initial_mel_generator import generate_roster_pdf
from roster_processor import roster_processor
from classes import PasCodeInfo, PasCodeSubmission
from constants import (
    REQUIRED_COLUMNS, OPTIONAL_COLUMNS, PDF_COLUMNS,
    cors_origins, allowed_types, images_dir, default_logo
)
from logging_config import LoggerSetup

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/upload/initial-mel")
async def upload_file(
        file: UploadFile = File(...),
        cycle: str = Form(...),
        year: int = Form(...)
):
    # Generate session ID early for logging
    session_id = str(uuid.uuid4())

    # Create session-specific logger
    logger = LoggerSetup.get_session_logger(session_id, cycle, year)

    logger.info(f"INITIAL MEL UPLOAD STARTED")
    logger.info(f"  Filename: {file.filename}")
    logger.info(f"  Content Type: {file.content_type}")
    logger.info(f"  Cycle: {cycle}")
    logger.info(f"  Year: {year}")

    return_object = {}

    if file.content_type not in allowed_types:
        error_msg = "Invalid file type. Only CSV or Excel files are allowed."
        logger.error(f"  FAILED: {error_msg}")
        logger.info(f"STATUS: FAILED - Invalid File Type")
        LoggerSetup.close_session_logger(session_id)
        return JSONResponse(content={"error": error_msg}, status_code=400)

    contents = await file.read()
    logger.info(f"  File size: {len(contents)} bytes")

    try:
        if file.filename.endswith(".csv"):
            logger.info(f"  Parsing CSV file")
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(".xlsx"):
            logger.info(f"  Parsing Excel file")
            df = pd.read_excel(io.BytesIO(contents))
        else:
            error_msg = "Unsupported file extension."
            logger.error(f"  FAILED: {error_msg}")
            logger.info(f"STATUS: FAILED - Unsupported Extension")
            LoggerSetup.close_session_logger(session_id)
            return JSONResponse(content={"error": error_msg}, status_code=400)

        logger.info(f"  File parsed successfully: {len(df)} rows, {len(df.columns)} columns")

        processed_df = df[REQUIRED_COLUMNS + OPTIONAL_COLUMNS]
        pdf_df = processed_df[PDF_COLUMNS]

        # Pass session_id to create_session so it uses our pre-generated ID
        create_session(processed_df, pdf_df, session_id=session_id)
        logger.info(f"  Session created: {session_id}")

        update_session(session_id, cycle=cycle)
        update_session(session_id, year=year)

        logger.info(f"  Starting roster processing...")
        roster_processor(df, session_id, cycle, year)
        logger.info(f"  Roster processing complete")

        session = get_session(session_id)

        # Use .get() to safely access session keys that might not exist
        if session.get('pascodes') is not None:
            return_object['pascodes'] = session['pascodes']
            logger.info(f"  PASCODEs found: {len(session['pascodes'])}")

        if session.get('pascode_unit_map') is not None:
            return_object['pascode_unit_map'] = session['pascode_unit_map']

        if session.get('small_unit_df') is not None:
            return_object['senior_rater_needed'] = True
            logger.info(f"  Senior rater required for small units")
        else:
            return_object["senior_rater_needed"] = False

        return_object['message'] = "Upload successful."
        return_object['session_id'] = session_id
        return_object['errors'] = session.get('error_log', [])

        if return_object['errors']:
            logger.warning(f"  Upload completed with {len(return_object['errors'])} errors")
        else:
            logger.info(f"  Upload completed successfully with no errors")

        logger.info(f"INITIAL MEL UPLOAD COMPLETED SUCCESSFULLY")

        return JSONResponse(content=return_object)

    except Exception as e:
        error_msg = f"Processing error: {str(e)}"
        logger.error(f"  EXCEPTION: {error_msg}", exc_info=True)
        logger.info(f"STATUS: FAILED - Exception")
        LoggerSetup.close_session_logger(session_id)
        return JSONResponse(content={"error": error_msg}, status_code=500)


@app.get("/api/download/initial-mel/{session_id}")
async def download_initial_mel(session_id: str):
    try:
        pdf_buffer: Optional[io.BytesIO] = get_pdf_from_redis(session_id)

        if not pdf_buffer:
            return JSONResponse(
                content={"error": "PDF not found for this session"},
                status_code=404
            )

        return StreamingResponse(
            pdf_buffer,
            media_type='application/pdf',
            headers={
                "Content-Disposition": f"attachment; filename=initial_mel_roster.pdf"
            }
        )
    except Exception as e:
        return JSONResponse(
            content={"error": f"Failed to retrieve PDF: {str(e)}"},
            status_code=500
        )

@app.get("/api/roster/preview/{session_id}")
async def get_roster_preview(
    session_id: str,
    category: str = "all",
    page: int = 1,
    page_size: int = 50
):
    """
    Get roster preview for review and editing.
    Returns all member data from the session including eligible,
    ineligible, discrepancy, BTZ, and small unit members.
    """
    try:
        session = get_session(session_id)

        if not session:
            return JSONResponse(
                content={"error": "Session not found or expired"},
                status_code=404
            )

        # Helper function to convert dataframes to list of dicts for JSON serialization
        def df_to_list(df):
            if df is None:
                return []
            # If it's already a list, return it
            if isinstance(df, list):
                return df
            # If it's a DataFrame, convert to dict records
            if hasattr(df, 'to_dict'):
                return df.to_dict('records')
            # Otherwise return empty list
            return []

        # Get all dataframes from session
        eligible_df = session.get('eligible_df', [])
        ineligible_df = session.get('ineligible_df', [])
        discrepancy_df = session.get('discrepancy_df', [])
        btz_df = session.get('btz_df', [])
        small_unit_df = session.get('small_unit_df', [])
        dataframe = session.get('dataframe', [])

        # Calculate statistics
        statistics = {
            "total_uploaded": len(df_to_list(dataframe)),
            "total_processed": (
                len(df_to_list(eligible_df)) +
                len(df_to_list(ineligible_df)) +
                len(df_to_list(discrepancy_df)) +
                len(df_to_list(btz_df))
            ),
            "eligible": len(df_to_list(eligible_df)),
            "ineligible": len(df_to_list(ineligible_df)),
            "discrepancy": len(df_to_list(discrepancy_df)),
            "btz": len(df_to_list(btz_df)),
            "errors": len(session.get('error_log', []))
        }

        # Build response
        response = {
            "session_id": session_id,
            "cycle": session.get('cycle', 'SSG'),
            "year": session.get('year', 2025),
            "edited": session.get('edited', False),
            "statistics": statistics,
            "categories": {
                "eligible": df_to_list(eligible_df),
                "ineligible": df_to_list(ineligible_df),
                "discrepancy": df_to_list(discrepancy_df),
                "btz": df_to_list(btz_df),
                "small_unit": df_to_list(small_unit_df)
            },
            "errors": session.get('error_log', []),
            "pascodes": session.get('pascodes', []),
            "pascode_unit_map": session.get('pascode_unit_map', {}),
            "custom_logo": {
                "uploaded": False,  # TODO: Implement logo storage
                "filename": None
            }
        }

        return JSONResponse(content=response)

    except Exception as e:
        return JSONResponse(
            content={"error": f"Failed to retrieve roster preview: {str(e)}"},
            status_code=500
        )


@app.put("/api/roster/member/{session_id}/{member_id}")
async def edit_roster_member(session_id: str, member_id: str, member_data: Dict):
    """
    Edit an existing member in the roster.
    Updates the member data in all relevant dataframes (eligible, ineligible, etc.)
    """
    try:
        session = get_session(session_id)

        if not session:
            return JSONResponse(
                content={"error": "Session not found or expired"},
                status_code=404
            )

        # Helper to update member in a dataframe
        def update_member_in_df(df, member_id_str, new_data):
            if df is None or not isinstance(df, pd.DataFrame):
                return df

            # Extract index from member_id (format: row_category_index or row_index)
            try:
                # Try to extract the last numeric part
                parts = member_id_str.split('_')
                index = int(parts[-1])

                if index < len(df):
                    # Update the row with new data
                    for key, value in new_data.items():
                        if key in df.columns:
                            df.at[index, key] = value
                    return df
            except (ValueError, IndexError):
                pass

            return df

        # Update member in all dataframes
        eligible_df = update_member_in_df(session.get('eligible_df'), member_id, member_data)
        ineligible_df = update_member_in_df(session.get('ineligible_df'), member_id, member_data)
        discrepancy_df = update_member_in_df(session.get('discrepancy_df'), member_id, member_data)
        btz_df = update_member_in_df(session.get('btz_df'), member_id, member_data)
        small_unit_df = update_member_in_df(session.get('small_unit_df'), member_id, member_data)
        pdf_dataframe = update_member_in_df(session.get('pdf_dataframe'), member_id, member_data)

        # Update session with modified dataframes
        if eligible_df is not None:
            update_session(session_id, eligible_df=eligible_df)
        if ineligible_df is not None:
            update_session(session_id, ineligible_df=ineligible_df)
        if discrepancy_df is not None:
            update_session(session_id, discrepancy_df=discrepancy_df)
        if btz_df is not None:
            update_session(session_id, btz_df=btz_df)
        if small_unit_df is not None:
            update_session(session_id, small_unit_df=small_unit_df)
        if pdf_dataframe is not None:
            update_session(session_id, pdf_dataframe=pdf_dataframe)

        # Mark session as edited
        update_session(session_id, edited=True)

        return JSONResponse(content={
            "success": True,
            "message": "Member updated successfully",
            "member_id": member_id
        })

    except Exception as e:
        return JSONResponse(
            content={"error": f"Failed to update member: {str(e)}"},
            status_code=500
        )


@app.post("/api/initial-mel/submit/pascode-info")
async def submit_pascode_info(payload: PasCodeSubmission):
    pascode_map = {pascode: info.model_dump() for pascode, info in payload.pascode_info.items()}
    if 'small_unit_sr' in pascode_map:
        small_unit_sr = pascode_map.pop('small_unit_sr')
    else:
        small_unit_sr = None

    if small_unit_sr:
        update_session(payload.session_id, small_unit_sr=small_unit_sr)
    update_session(payload.session_id, pascode_map=pascode_map)
    srid_pascode_map = {}
    session = get_session(payload.session_id)

    # Validate session exists
    if not session:
        return JSONResponse(
            content={"error": "Session not found or expired"},
            status_code=404
        )

    # Validate required keys exist
    if 'pascodes' not in session or 'pascode_map' not in session:
        return JSONResponse(
            content={"error": "Invalid session data - missing required keys"},
            status_code=400
        )

    for pascode in session['pascodes']:
        # Validate pascode exists in pascode_map
        if pascode not in session['pascode_map']:
            continue
        # Validate srid exists in pascode info
        if 'srid' not in session['pascode_map'][pascode]:
            continue
        srid = session['pascode_map'][pascode]['srid']
        if srid in srid_pascode_map:
            srid_pascode_map[srid].append(pascode)
        else:
            srid_pascode_map[srid] = [pascode]

    update_session(payload.session_id, srid_pascode_map=srid_pascode_map)

    # Use constants for logo path
    logo_path = os.path.join(images_dir, default_logo)

    response = generate_roster_pdf(payload.session_id,
                                   output_filename=rf"tmp/{payload.session_id}_initial_mel_roster.pdf",
                                   logo_path=logo_path)

    if response:
        return response
    return JSONResponse(content={"error": "PDF generation failed"}, status_code=500)


@app.post("/api/upload/final-mel")
async def upload_final_mel_file(
        file: UploadFile = File(...),
        cycle: str = Form(...),
        year: int = Form(...)
):
    # Generate session ID early for logging
    session_id = str(uuid.uuid4())

    # Create session-specific logger
    logger = LoggerSetup.get_session_logger(session_id, cycle, year)

    logger.info(f"FINAL MEL UPLOAD STARTED")
    logger.info(f"  Filename: {file.filename}")
    logger.info(f"  Content Type: {file.content_type}")
    logger.info(f"  Cycle: {cycle}")
    logger.info(f"  Year: {year}")

    return_object = {}

    if file.content_type not in allowed_types:
        error_msg = "Invalid file type. Only CSV or Excel files are allowed."
        logger.error(f"  FAILED: {error_msg}")
        logger.info(f"STATUS: FAILED - Invalid File Type")
        LoggerSetup.close_session_logger(session_id)
        return JSONResponse(content={"error": error_msg}, status_code=400)

    contents = await file.read()
    logger.info(f"  File size: {len(contents)} bytes")

    try:
        if file.filename.endswith(".csv"):
            logger.info(f"  Parsing CSV file")
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(".xlsx"):
            logger.info(f"  Parsing Excel file")
            df = pd.read_excel(io.BytesIO(contents))
        else:
            error_msg = "Unsupported file extension."
            logger.error(f"  FAILED: {error_msg}")
            logger.info(f"STATUS: FAILED - Unsupported Extension")
            LoggerSetup.close_session_logger(session_id)
            return JSONResponse(content={"error": error_msg}, status_code=400)

        logger.info(f"  File parsed successfully: {len(df)} rows, {len(df.columns)} columns")

        processed_df = df[REQUIRED_COLUMNS + OPTIONAL_COLUMNS]
        pdf_df = processed_df[PDF_COLUMNS]

        # Pass session_id to create_session so it uses our pre-generated ID
        create_session(processed_df, pdf_df, session_id=session_id)
        logger.info(f"  Session created: {session_id}")

        update_session(session_id, cycle=cycle)
        update_session(session_id, year=year)

        logger.info(f"  Starting roster processing...")
        roster_processor(df, session_id, cycle, year)
        logger.info(f"  Roster processing complete")

        session = get_session(session_id)

        # Use .get() to safely access session keys that might not exist
        if session.get('pascodes') is not None:
            return_object['pascodes'] = session['pascodes']
            logger.info(f"  PASCODEs found: {len(session['pascodes'])}")

        if session.get('pascode_unit_map') is not None:
            return_object['pascode_unit_map'] = session['pascode_unit_map']

        if session.get('small_unit_df') is not None:
            return_object['senior_rater_needed'] = True
            logger.info(f"  Senior rater required for small units")
        else:
            return_object["senior_rater_needed"] = False

        return_object['message'] = "Upload successful."
        return_object['session_id'] = session_id
        return_object['errors'] = session.get('error_log', [])

        if return_object['errors']:
            logger.warning(f"  Upload completed with {len(return_object['errors'])} errors")
        else:
            logger.info(f"  Upload completed successfully with no errors")

        logger.info(f"FINAL MEL UPLOAD COMPLETED SUCCESSFULLY")

        return JSONResponse(content=return_object)

    except Exception as e:
        error_msg = f"Processing error: {str(e)}"
        logger.error(f"  EXCEPTION: {error_msg}", exc_info=True)
        logger.info(f"STATUS: FAILED - Exception")
        LoggerSetup.close_session_logger(session_id)
        return JSONResponse(content={"error": error_msg}, status_code=500)


@app.post("/api/final-mel/submit/pascode-info")
async def submit_final_pascode_info(payload: PasCodeSubmission):
    pascode_map = {pascode: info.model_dump() for pascode, info in payload.pascode_info.items()}
    if 'small_unit_sr' in pascode_map:
        small_unit_sr = pascode_map.pop('small_unit_sr')
    else:
        small_unit_sr = None

    if small_unit_sr:
        update_session(payload.session_id, small_unit_sr=small_unit_sr)
    update_session(payload.session_id, pascode_map=pascode_map)
    srid_pascode_map = {}
    session = get_session(payload.session_id)

    # Validate session exists
    if not session:
        return JSONResponse(
            content={"error": "Session not found or expired"},
            status_code=404
        )

    # Validate required keys exist
    if 'pascodes' not in session or 'pascode_map' not in session:
        return JSONResponse(
            content={"error": "Invalid session data - missing required keys"},
            status_code=400
        )

    for pascode in session['pascodes']:
        # Validate pascode exists in pascode_map
        if pascode not in session['pascode_map']:
            continue
        # Validate srid exists in pascode info
        if 'srid' not in session['pascode_map'][pascode]:
            continue
        srid = session['pascode_map'][pascode]['srid']
        if srid in srid_pascode_map:
            srid_pascode_map[srid].append(pascode)
        else:
            srid_pascode_map[srid] = [pascode]

    update_session(payload.session_id, srid_pascode_map=srid_pascode_map)

    # Use constants for logo path
    logo_path = os.path.join(images_dir, default_logo)

    response = generate_final_roster_pdf(payload.session_id,
                                         output_filename=rf"tmp/{payload.session_id}_final_mel_roster.pdf",
                                         logo_path=logo_path)

    if response:
        return response
    return JSONResponse(content={"error": "PDF generation failed"}, status_code=500)


@app.get("/api/download/final-mel/{session_id}")
async def download_final_mel(session_id: str):
    try:
        pdf_buffer: Optional[io.BytesIO] = get_pdf_from_redis(session_id)

        if not pdf_buffer:
            return JSONResponse(
                content={"error": "PDF not found for this session"},
                status_code=404
            )

        return StreamingResponse(
            pdf_buffer,
            media_type='application/pdf',
            headers={
                "Content-Disposition": f"attachment; filename=final_mel_roster.pdf"
            }
        )
    except Exception as e:
        return JSONResponse(
            content={"error": f"Failed to retrieve PDF: {str(e)}"},
            status_code=500
        )