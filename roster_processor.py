# In roster_processor.py

import pandas as pd
from accounting_date_check import accounting_date_check
from board_filter import board_filter
from session_manager import update_session, get_session
from constants import (
    REQUIRED_COLUMNS, OPTIONAL_COLUMNS, PDF_COLUMNS,
    GRADE_MAP, PROMOTIONAL_MAP, small_unit_threshold, max_unit_length,
    OFFICER_RANKS, ENLISTED_RANKS
)

from datetime import datetime
from date_parsing import parse_date
from logging_config import LoggerSetup, mask_name, mask_ssan

def format_date_for_display(date_value):
    """Format date for display in PDFs as DD-MMM-YYYY"""
    if pd.isna(date_value) or date_value is None:
        return None

    if isinstance(date_value, str):
        parsed_date = parse_date(date_value)
        if parsed_date:
            return parsed_date.strftime("%d-%b-%Y").upper()
        return date_value

    if isinstance(date_value, (datetime, pd.Timestamp)):
        return date_value.strftime("%d-%b-%Y").upper()

    return str(date_value)

def roster_processor(roster_df, session_id, cycle, year):
    # Create session-specific logger
    logger = LoggerSetup.get_session_logger(session_id, cycle, year)
    logger.info(f"Processing roster with {len(roster_df)} total members")

    eligible_service_members = []
    eligible_btz_service_members = []
    ineligible_service_members = []
    small_unit_eligible_service_members = []
    discrepancy_service_members = []


    pascodes = []
    small_unit_pascodes = []
    reason_for_ineligible_map = {}
    pascodeUnitMap = {}
    unit_total_map = {}

    error_log = []

    all_roster_columns = REQUIRED_COLUMNS + OPTIONAL_COLUMNS

    missing_columns = [col for col in all_roster_columns if col not in roster_df.columns]
    if missing_columns:
        error_msg = f"Missing required columns: {', '.join(missing_columns)}"
        error_log.append(error_msg)
        logger.error(error_msg)
        logger.info(f"STATUS: FAILED - {error_msg}")
        update_session(session_id, error_log=error_log)
        LoggerSetup.close_session_logger(session_id)
        return

    filtered_roster_df = roster_df[all_roster_columns].copy()
    logger.info(f"Roster filtered to required columns. Processing {len(filtered_roster_df)} members.")

    # Parse all date columns in the DataFrame ONCE, before processing
    date_columns = ['DOR', 'UIF_DISPOSITION_DATE', 'TAFMSD', 'DATE_ARRIVED_STATION']
    for col in date_columns:
        if col in filtered_roster_df.columns:
            filtered_roster_df[col] = filtered_roster_df[col].apply(
                lambda x: parse_date(x, error_log, None)
            )

    # Processing loop - now working with properly parsed datetime objects
    logger.info("=" * 80)
    logger.info("STARTING MEMBER-BY-MEMBER PROCESSING")
    logger.info("=" * 80)

    for index, row in filtered_roster_df.iterrows():
        member_name = row.get('FULL_NAME', 'Unknown')
        ssan = row.get('SSAN', 'N/A')
        grade = row.get('GRADE', 'Unknown')

        # Check for officer ranks - skip silently
        if row['GRADE'] in OFFICER_RANKS:
            msg = f"Officer {row['FULL_NAME']} ({row['GRADE']}) excluded from enlisted promotion processing"
            error_log.append(msg)
            continue

        # Skip unknown ranks - skip silently
        if row['GRADE'] not in ENLISTED_RANKS:
            msg = f"Unknown or unsupported rank: {row['GRADE']} for {row['FULL_NAME']}"
            error_log.append(msg)
            continue

        # Check projected grades FIRST - this determines if they should be on the roster
        # CRITICAL FIX: Use .get() for optional columns to prevent KeyError
        projected_grade = row.get('GRADE_PERM_PROJ')

        # If projected for next grade (e.g., MSG when cycle is TSG), exclude completely - skip silently
        if projected_grade == PROMOTIONAL_MAP.get(cycle):
            continue

        # Check if member should be included in this cycle's roster
        # Include if: (1) current grade matches cycle OR (2) projected for this cycle
        has_projected_grade = projected_grade == cycle
        grade_matches_cycle = row['GRADE'] == cycle or (row['GRADE'] == 'A1C' and cycle == 'SRA')

        # Skip if wrong cycle - skip silently
        if not (grade_matches_cycle or has_projected_grade):
            continue

        # Check accounting date - those who fail should be excluded completely - skip silently
        valid_member = accounting_date_check(row['DATE_ARRIVED_STATION'], cycle, year, logger=None)
        if not valid_member:
            continue

        # ONLY log members that will appear on the roster (passed all initial filters)
        # Use PII masking for CUI compliance
        logger.info(f"\n{'='*60}")
        logger.info(f"ROW {index}: Processing {mask_name(member_name)} (SSAN: {mask_ssan(ssan)})")
        logger.info(f"  Current Grade: {grade}")
        logger.info(f"  Promotion Cycle: {cycle} {year}")
        logger.info(f"  Projected Grade: {projected_grade if projected_grade else 'None'}")
        logger.info(f"  ✓ Grade matches cycle or projected for cycle")
        logger.info(f"  ✓ Accounting date check passed")

        # Check for missing required data
        missing_required = False
        for column in REQUIRED_COLUMNS:
            if column in row and pd.isna(row[column]):
                error_log.append(f"Missing required data at row {index}, column {column}")
                logger.warning(f"  ❌ Missing required column: {column}")
                missing_required = True
                break

        if missing_required:
            ineligible_service_members.append(index)
            reason_for_ineligible_map[index] = 'Missing required data'
            logger.info(f"  Decision: Marked as ineligible (Missing Required Data)")
            continue

        logger.info(f"  ✓ All required data present")

        # If already projected for this cycle, mark as ineligible
        if has_projected_grade:
            ineligible_service_members.append(index)
            reason_for_ineligible_map[index] = f'Projected for {cycle}.'
            logger.info(f"  ❌ INELIGIBLE: Already projected for {cycle}")
            logger.info(f"  Decision: Marked as ineligible (Already Projected)")
            continue

        # Track PASCODEs
        if row['ASSIGNED_PAS'] not in pascodes:
            pascodes.append(row['ASSIGNED_PAS'])
            pascodeUnitMap[row['ASSIGNED_PAS']] = row['ASSIGNED_PAS_CLEARTEXT']

        logger.info(f"  ✓ Ready for board filter - calling board_filter() for detailed eligibility check")

        # Board filter check - pass member info and logger for logging
        # Note: member_name and ssan already defined above
        member_status = board_filter(row['GRADE'], year, row['DOR'], row['UIF_CODE'],
                                     row['UIF_DISPOSITION_DATE'], row['TAFMSD'], row['REENL_ELIG_STATUS'],
                                     row['PAFSC'], row['2AFSC'], row['3AFSC'], row['4AFSC'],
                                     member_name=member_name, ssan=ssan, logger=logger)

        if member_status is None:
            logger.info(f"  Decision: Not eligible (returned None from board_filter)")
            continue

        # Handle tuple or list cases
        elif isinstance(member_status, (tuple, list)):
            # Validate tuple has at least one element before accessing
            if len(member_status) == 0:
                logger.warning(f"  ⚠️ WARNING: Empty tuple returned from board_filter")
                continue

            # Case: discrepancy (tuple of strings)
            if isinstance(member_status[0], str) and member_status[0] == 'discrepancy':
                eligible_service_members.append(index)
                discrepancy_service_members.append(index)
                # Update unit_total_map for discrepancy members (they're still eligible)
                unit_total_map[row['ASSIGNED_PAS']] = unit_total_map.get(row['ASSIGNED_PAS'], 0) + 1
                if len(member_status) > 1:
                    reason_for_ineligible_map[index] = member_status[1]
                logger.info(f"  ✅ ELIGIBLE (WITH DISCREPANCY): {member_status[1] if len(member_status) > 1 else 'No reason provided'}")
                logger.info(f"  Decision: Added to eligible roster with discrepancy flag")

            # Case: BTZ eligible (True, 'btz')
            elif member_status[0] is True and len(member_status) > 1 and member_status[1] == 'btz':
                eligible_btz_service_members.append(index)
                # Update unit_total_map for BTZ members
                unit_total_map[row['ASSIGNED_PAS']] = unit_total_map.get(row['ASSIGNED_PAS'], 0) + 1
                logger.info(f"  ✅ ELIGIBLE (BTZ): Below-the-Zone eligibility")
                logger.info(f"  Decision: Added to BTZ eligible roster")

            # Case: ineligible (False, reason)
            elif member_status[0] is False:
                ineligible_service_members.append(index)
                if len(member_status) > 1:
                    reason_for_ineligible_map[index] = member_status[1]
                    logger.info(f"  ❌ INELIGIBLE: {member_status[1]}")
                else:
                    logger.info(f"  ❌ INELIGIBLE: No specific reason provided")
                logger.info(f"  Decision: Added to ineligible roster")

        # Handle plain True (no tuple)
        elif member_status is True:
            eligible_service_members.append(index)
            unit_total_map[row['ASSIGNED_PAS']] = unit_total_map.get(row['ASSIGNED_PAS'], 0) + 1
            logger.info(f"  ✅ ELIGIBLE: Meets all requirements")
            logger.info(f"  Decision: Added to eligible roster")

    pascodes = sorted(pascodes)
    update_session(session_id, pascodes=pascodes)

    # Create PDF DataFrames with parsed datetime objects
    pdf_roster = filtered_roster_df[PDF_COLUMNS].copy()

    eligible_df = pdf_roster.loc[eligible_service_members].copy() if eligible_service_members else pd.DataFrame()
    ineligible_df = pdf_roster.loc[ineligible_service_members].copy() if ineligible_service_members else pd.DataFrame()
    discrepancy_df = pdf_roster.loc[discrepancy_service_members].copy() if discrepancy_service_members else pd.DataFrame()
    btz_df = pdf_roster.loc[eligible_btz_service_members].copy() if eligible_btz_service_members else pd.DataFrame()

    if not ineligible_df.empty:
        ineligible_df['REASON'] = ineligible_df.index.map(reason_for_ineligible_map)
    if not discrepancy_df.empty:
        discrepancy_df['REASON'] = discrepancy_df.index.map(reason_for_ineligible_map)

    # NOW format dates for display - only when preparing final output
    def format_df_for_session(df):
        if df.empty:
            return df
        df_copy = df.copy()

        # Format date columns for display ONLY
        date_columns = ['DOR', 'TAFMSD', 'DATE_ARRIVED_STATION']
        for col in date_columns:
            if col in df_copy.columns:
                df_copy[col] = df_copy[col].apply(format_date_for_display)

        # Format text columns
        if 'ASSIGNED_PAS_CLEARTEXT' in df_copy.columns:
            df_copy['ASSIGNED_PAS_CLEARTEXT'] = df_copy['ASSIGNED_PAS_CLEARTEXT'].str[:max_unit_length]
        if 'FULL_NAME' in df_copy.columns:
            df_copy['FULL_NAME'] = df_copy['FULL_NAME'].str[:max_unit_length]
        return df_copy

    # Apply formatting only for final output
    eligible_df = format_df_for_session(eligible_df)
    ineligible_df = format_df_for_session(ineligible_df)
    discrepancy_df = format_df_for_session(discrepancy_df)
    btz_df = format_df_for_session(btz_df)

    for pascode in unit_total_map:
        if cycle == 'MSG' or cycle == 'SMS':
            small_unit_pascodes.append(pascode)
        elif unit_total_map[pascode] <= small_unit_threshold:
            small_unit_pascodes.append(pascode)

    if not eligible_df.empty:
        small_unit_eligible_service_members = eligible_df[eligible_df['ASSIGNED_PAS'].isin(small_unit_pascodes)].index
        small_unit_df = eligible_df.loc[small_unit_eligible_service_members].copy()
    else:
        small_unit_df = pd.DataFrame()

    # Update session with results
    update_session(session_id, eligible_df=eligible_df)
    update_session(session_id, ineligible_df=ineligible_df)
    update_session(session_id, discrepancy_df=discrepancy_df)
    update_session(session_id, btz_df=btz_df)
    update_session(session_id, small_unit_df=small_unit_df)

    if pascodeUnitMap:
        update_session(session_id, pascode_unit_map=pascodeUnitMap)

    if error_log:
        update_session(session_id, error_log=error_log)

    # Calculate members on roster
    total_on_roster = (len(eligible_service_members) + len(eligible_btz_service_members) +
                      len(ineligible_service_members))
    total_skipped = len(filtered_roster_df) - total_on_roster

    # Log summary statistics
    logger.info("")
    logger.info("=" * 80)
    logger.info("PROCESSING SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total Members in Upload: {len(filtered_roster_df)}")
    logger.info(f"Members on Roster (logged above): {total_on_roster}")
    logger.info(f"Members Skipped (not matching cycle/accounting date): {total_skipped}")
    logger.info("")
    logger.info("ROSTER BREAKDOWN:")
    logger.info(f"  • Eligible Members: {len(eligible_service_members)}")
    logger.info(f"  • BTZ Eligible Members: {len(eligible_btz_service_members)}")
    logger.info(f"  • Ineligible Members: {len(ineligible_service_members)}")
    logger.info(f"  • Discrepancy Members: {len(discrepancy_service_members)}")
    logger.info("")
    logger.info(f"PASCODEs (Units) Found: {len(pascodes)}")
    logger.info(f"Small Units Requiring Senior Rater: {len(small_unit_pascodes)}")
    if error_log:
        logger.warning(f"Errors Encountered: {len(error_log)}")

    logger.info(f"STATUS: SUCCESS")

    # Close the session logger
    LoggerSetup.close_session_logger(session_id)

    return


def recalculate_small_units(session_id):
    """
    Recalculate small_unit_df after add/edit/delete operations.
    This ensures senior_rater_needed flag is correctly set based on current data.
    """
    session = get_session(session_id)
    if not session:
        return

    cycle = session.get('cycle', 'SSG')
    eligible_df = session.get('eligible_df', pd.DataFrame())

    # Convert to DataFrame if it's a list
    if isinstance(eligible_df, list):
        eligible_df = pd.DataFrame(eligible_df)

    # If no eligible members, clear small_unit_df
    if eligible_df.empty:
        update_session(session_id, small_unit_df=pd.DataFrame())
        return

    # Count eligible members per pascode
    unit_total_map = {}
    for _, row in eligible_df.iterrows():
        pascode = row.get('ASSIGNED_PAS', '')
        if pascode:
            unit_total_map[pascode] = unit_total_map.get(pascode, 0) + 1

    # Determine which pascodes are small units
    small_unit_pascodes = []
    for pascode in unit_total_map:
        if cycle == 'MSG' or cycle == 'SMS':
            # MSG and SMS cycles: all units are small units
            small_unit_pascodes.append(pascode)
        elif unit_total_map[pascode] <= small_unit_threshold:
            # Other cycles: units with <= threshold eligible members
            small_unit_pascodes.append(pascode)

    # Extract small unit members from eligible_df
    if small_unit_pascodes:
        small_unit_df = eligible_df[eligible_df['ASSIGNED_PAS'].isin(small_unit_pascodes)].copy()
    else:
        small_unit_df = pd.DataFrame()

    # Update session with the recalculated small_unit_df
    update_session(session_id, small_unit_df=small_unit_df)