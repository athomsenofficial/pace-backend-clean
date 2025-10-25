from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
from date_parsing import parse_date
from constants import (
    SCODS, TIG, TIG_MONTHS_REQUIRED, TAFMSD, MDOS,
    MAIN_HIGHER_TENURE, EXCEPTION_HIGHER_TENURE, PAFSC_MAP,
    RE_CODES, hyt_start_date, hyt_end_date
)
from typing import Union, Tuple, Optional
from logging import Logger

def pafsc_check(grade: str, pafsc: Optional[str], two_afsc: Optional[str],
                 three_afsc: Optional[str], four_afsc: Optional[str]) -> Optional[bool]:
    """
    Check if any AFSC meets the required skill level for the grade.

    Returns:
        True if meets requirement, False if doesn't, None if AFSC is 8/9 prefixed
    """
    # Handle NaN/None values - convert to None
    if pd.isna(pafsc):
        pafsc = None
    if pd.isna(two_afsc):
        two_afsc = None
    if pd.isna(three_afsc):
        three_afsc = None
    if pd.isna(four_afsc):
        four_afsc = None

    # Check for special AFSCs (8/9 prefix)
    if pafsc and isinstance(pafsc, str) and len(pafsc) > 0 and pafsc[0] in ('8', '9'):
        return None

    required_level = PAFSC_MAP.get(grade)
    if not required_level:
        return False

    afscs = [pafsc, two_afsc, three_afsc, four_afsc]

    for afsc in afscs:
        # Skip None or NaN values
        if afsc is None or pd.isna(afsc):
            continue
        if isinstance(afsc, str) and len(afsc) >= 5:
            skill_level_index = 4 if afsc[0].isalpha() or afsc[0] == '-' else 3

            try:
                if afsc[skill_level_index] >= required_level:
                    return True
            except IndexError:
                continue

    return False

def btz_elgibility_check(date_of_rank, year):
    date_of_rank = parse_date(date_of_rank)
    if not date_of_rank:
        return False
    cutoff_date = datetime.strptime(f"01-Feb-{year}", "%d-%b-%Y")
    btz_date_of_rank = date_of_rank + relativedelta(months=22)
    scod_date = datetime.strptime(f"{SCODS.get('SRA')}-{year}", "%d-%b-%Y")
    if btz_date_of_rank <= cutoff_date:
        return True
    if cutoff_date < btz_date_of_rank <= scod_date:
        return True
    return False

def check_a1c_eligbility(date_of_rank, year):
    date_of_rank = parse_date(date_of_rank)
    if not date_of_rank:
        return False
    cutoff_date = datetime.strptime(f"01-Feb-{year}", "%d-%b-%Y")
    scod_date = datetime.strptime(f"{SCODS.get('SRA')}-{year}", "%d-%b-%Y")
    standard_a1c_date_of_rank = date_of_rank + relativedelta(months=28)
    if standard_a1c_date_of_rank <= cutoff_date:
        return True
    if cutoff_date < standard_a1c_date_of_rank <= scod_date:
        return False
    return None

def three_year_tafmsd_check(scod_as_datetime, tafmsd):
    tafmsd = parse_date(tafmsd)
    if tafmsd is None:
        return False
    adjusted_tafmsd = tafmsd + relativedelta(months=36)
    # Return True if they WILL have more than 36 months TIS by SCOD (ineligible)
    return adjusted_tafmsd <= scod_as_datetime

def board_filter(
    grade: str,
    year: int,
    date_of_rank: Union[str, datetime, None],
    uif_code: Union[int, float, str, None],
    uif_disposition_date: Union[str, datetime, None],
    tafmsd: Union[str, datetime, None],
    re_status: Optional[str],
    pafsc: Optional[str],
    two_afsc: Optional[str],
    three_afsc: Optional[str],
    four_afsc: Optional[str],
    member_name: str = "Unknown",
    ssan: str = "N/A",
    logger: Optional[Logger] = None
) -> Union[bool, Tuple[bool, str], Tuple[str, str], None]:
    """
    Filter members for board eligibility with comprehensive logging.

    Args:
        grade: Member's current grade
        year: Board year
        date_of_rank: Date member received current rank
        uif_code: Unfavorable Information File code (can be NaN)
        uif_disposition_date: UIF disposition date (can be None/NaN)
        tafmsd: Total Active Federal Military Service Date
        re_status: Reenlistment Eligibility status code (can be None/NaN)
        pafsc: Primary Air Force Specialty Code (can be None/NaN)
        two_afsc: Second AFSC (can be None/NaN)
        three_afsc: Third AFSC (can be None/NaN)
        four_afsc: Fourth AFSC (can be None/NaN)
        member_name: Member's name (for logging)
        ssan: Member's SSAN (for logging)
        logger: Logger instance (optional, if None no logging)

    Returns:
        True: Eligible
        False, reason: Ineligible with reason
        'discrepancy', reason: Eligible with discrepancy flag
        True, 'btz': BTZ eligible
        None: Not eligible for consideration
    """
    try:
        # Helper functions for conditional logging
        def log_info(msg):
            if logger:
                logger.info(msg)

        def log_warning(msg):
            if logger:
                logger.warning(msg)

        def log_error(msg, exc_info=False):
            if logger:
                logger.error(msg, exc_info=exc_info)

        log_info(f"{'='*60}")
        log_info(f"PROCESSING: {member_name} (SSAN: {ssan})")
        log_info(f"Grade: {grade} | Year: {year}")
        log_info(f"Input Data - DOR: {date_of_rank}, TAFMSD: {tafmsd}, UIF: {uif_code}")

        # Step 1: Parse dates
        log_info(f"Step 1: Parsing dates")
        date_of_rank = parse_date(date_of_rank)
        uif_disposition_date = parse_date(uif_disposition_date)
        tafmsd = parse_date(tafmsd)
        log_info(f"  Parsed DOR: {date_of_rank}")
        log_info(f"  Parsed TAFMSD: {tafmsd}")
        log_info(f"  Parsed UIF Disposition: {uif_disposition_date}")

        # REMOVED the strict None check that was causing all members to be ineligible
        # Only check for required dates that must be present
        if date_of_rank is None or tafmsd is None:
            reason = 'Required date missing or unreadable'
            log_warning(f"  FAILED: {reason}")
            log_info(f"{'='*60}\n")
            return False, reason

        # Step 2: Calculate key dates
        log_info(f"Step 2: Calculating key dates and thresholds")
        # Determine SCOD year based on month
        scod_month_day = SCODS.get(grade)  # e.g., '31-JAN'
        month_name = scod_month_day.split('-')[1]  # e.g., 'JAN'

        # SCODs in Jan-Mar use year+1, others use year
        if month_name in ['JAN', 'FEB', 'MAR']:
            scod_year = year + 1
        else:
            scod_year = year

        scod = f'{scod_month_day}-{scod_year}'
        scod_as_datetime = datetime.strptime(scod, "%d-%b-%Y")
        log_info(f"  SCOD (Selection Cutoff Date): {scod_as_datetime.strftime('%d-%b-%Y')}")

        tig_selection_month = f'{TIG.get(grade)}-{year + 1}'
        formatted_tig_selection_month = datetime.strptime(tig_selection_month, "%d-%b-%Y")
        tig_eligibility_month = formatted_tig_selection_month - relativedelta(months=TIG_MONTHS_REQUIRED.get(grade))
        log_info(f"  TIG Eligibility Month: {tig_eligibility_month.strftime('%d-%b-%Y')} (requires {TIG_MONTHS_REQUIRED.get(grade)} months TIG)")

        tafmsd_years = TAFMSD.get(grade)
        if tafmsd_years < 1:
            months_total = int(tafmsd_years * 12)
            tafmsd_required_date = formatted_tig_selection_month - relativedelta(months=months_total)
        else:
            months_component = int((tafmsd_years % 1) * 12)
            years_component = int(tafmsd_years)
            tafmsd_required_date = formatted_tig_selection_month - relativedelta(years=years_component,
                                                                                 months=months_component)
        log_info(f"  TAFMSD Required Date: {tafmsd_required_date.strftime('%d-%b-%Y')} (requires {tafmsd_years} years TIS)")

        hyt_years = MAIN_HIGHER_TENURE.get(grade)
        if hyt_years < 1:
            hyt_months_total = int(hyt_years * 12)
            hyt_date = tafmsd + relativedelta(months=hyt_months_total)
        else:
            hyt_months_component = int((hyt_years % 1) * 12)
            hyt_years_component = int(hyt_years)
            hyt_date = tafmsd + relativedelta(years=hyt_years_component, months=hyt_months_component)
        log_info(f"  HYT Date: {hyt_date.strftime('%d-%b-%Y')} ({hyt_years} years)")

        mdos_month = f'{MDOS.get(grade)}-{year + 1}'
        mdos = datetime.strptime(mdos_month, "%d-%b-%Y")
        log_info(f"  MDOS (Mandatory Date of Separation): {mdos.strftime('%d-%b-%Y')}")

        btz_check = None

        # Step 3: A1C specific checks
        if grade == 'A1C':
            log_info(f"Step 3: A1C Eligibility Check")
            eligibility_status = check_a1c_eligbility(date_of_rank, year)
            log_info(f"  A1C eligibility status: {eligibility_status}")
            if eligibility_status is None:
                log_info(f"  Checking BTZ eligibility for A1C")
                btz_check = btz_elgibility_check(date_of_rank, year)
                log_info(f"  BTZ check result: {btz_check}")
                if not btz_check:
                    log_warning(f"  FAILED: BTZ check failed for A1C")
                    log_info(f"{'='*60}\n")
                    return None
            elif eligibility_status is False:
                reason = 'Failed A1C Check.'
                log_warning(f"  FAILED: {reason}")
                log_info(f"{'='*60}\n")
                return False, reason
        else:
            log_info(f"Step 3: Skipping A1C check (not applicable for {grade})")

        # Step 4: 3-year TIS check for junior enlisted
        if grade in ('A1C', 'AMN', 'AB'):
            log_info(f"Step 4: 3-Year TIS Check for {grade}")
            if three_year_tafmsd_check(scod_as_datetime, tafmsd):
                reason = 'SRA 2 Feb - 31 Mar or 3yr TIS'
                log_warning(f"  FAILED: {reason}")
                log_info(f"{'='*60}\n")
                return False, reason
            log_info(f"  PASSED: 3-year TIS check")
        else:
            log_info(f"Step 4: Skipping 3-year TIS check (not applicable for {grade})")

        # Step 5: TIG check
        log_info(f"Step 5: Time in Grade (TIG) Check")
        if date_of_rank is None or date_of_rank > tig_eligibility_month:
            reason = f'TIG: < {TIG_MONTHS_REQUIRED.get(grade)} months'
            log_warning(f"  FAILED: DOR {date_of_rank.strftime('%d-%b-%Y') if date_of_rank else 'None'} is after required {tig_eligibility_month.strftime('%d-%b-%Y')}")
            log_info(f"{'='*60}\n")
            return False, reason
        log_info(f"  PASSED: DOR {date_of_rank.strftime('%d-%b-%Y')} is before {tig_eligibility_month.strftime('%d-%b-%Y')}")

        # Step 6: TIS check
        log_info(f"Step 6: Time in Service (TIS) Check")
        if tafmsd > tafmsd_required_date:
            reason = f'TIS < {TAFMSD.get(grade)} years'
            log_warning(f"  FAILED: TAFMSD {tafmsd.strftime('%d-%b-%Y')} is after required {tafmsd_required_date.strftime('%d-%b-%Y')}")
            log_info(f"{'='*60}\n")
            return False, reason
        log_info(f"  PASSED: TAFMSD {tafmsd.strftime('%d-%b-%Y')} is before {tafmsd_required_date.strftime('%d-%b-%Y')}")

        # Step 7: HYT check with exception handling
        log_info(f"Step 7: High Year of Tenure (HYT) Check")
        if hyt_start_date < hyt_date < hyt_end_date:
            exception_hyt_years = EXCEPTION_HIGHER_TENURE.get(grade, MAIN_HIGHER_TENURE.get(grade))
            log_info(f"  Applying HYT exception: {exception_hyt_years} years")
            hyt_date = tafmsd + relativedelta(years=exception_hyt_years)
            log_info(f"  New HYT date: {hyt_date.strftime('%d-%b-%Y')}")
        if hyt_date < mdos:
            reason = 'Higher tenure.'
            log_warning(f"  FAILED: HYT date {hyt_date.strftime('%d-%b-%Y')} is before MDOS {mdos.strftime('%d-%b-%Y')}")
            log_info(f"{'='*60}\n")
            return False, reason
        log_info(f"  PASSED: HYT date {hyt_date.strftime('%d-%b-%Y')} is after MDOS {mdos.strftime('%d-%b-%Y')}")

        # Step 8: UIF check
        log_info(f"Step 8: UIF Code Check")
        # Handle NaN/None/empty UIF code
        if pd.isna(uif_code) or uif_code is None or uif_code == '':
            uif_code = 0
            log_info(f"  UIF Code: 0 (no UIF or empty value)")
        else:
            try:
                uif_code = int(uif_code)
                log_info(f"  UIF Code: {uif_code}")
            except (TypeError, ValueError):
                uif_code = 0
                log_info(f"  UIF Code: 0 (invalid value converted to 0)")
        # Allow uif_disposition_date to be None since it's optional
        if uif_code > 1 and uif_disposition_date and uif_disposition_date < scod_as_datetime:
            reason = f'UIF code: {uif_code}'
            log_warning(f"  DISCREPANCY: {reason} with disposition date {uif_disposition_date.strftime('%d-%b-%Y')} before SCOD")
            log_info(f"{'='*60}\n")
            return 'discrepancy', reason
        log_info(f"  PASSED: No UIF issues")

        # Step 9: RE status check
        log_info(f"Step 9: Reenlistment Eligibility (RE) Status Check")
        # Handle NaN/None for RE status
        if pd.isna(re_status) or re_status is None:
            re_status = None
            log_info(f"  RE Status: None (empty or not provided)")
        else:
            log_info(f"  RE Status: {re_status}")
        # Only check if RE status is not None
        if re_status and re_status in RE_CODES.keys():
            reason = f'{re_status}: {RE_CODES.get(re_status)}'
            log_warning(f"  DISCREPANCY: {reason}")
            log_info(f"{'='*60}\n")
            return 'discrepancy', reason
        log_info(f"  PASSED: RE status is acceptable")

        # Step 10: PAFSC skill level check
        log_info(f"Step 10: PAFSC Skill Level Check")
        if grade not in ('SMS', 'MSG'):
            log_info(f"  Checking PAFSC: {pafsc}, 2nd: {two_afsc}, 3rd: {three_afsc}, 4th: {four_afsc}")
            pafsc_result = pafsc_check(grade, pafsc, two_afsc, three_afsc, four_afsc)
            log_info(f"  PAFSC check result: {pafsc_result}")
            if pafsc_result is False:
                reason = 'Insufficient PAFSC skill level.'
                log_warning(f"  DISCREPANCY: {reason}")
                log_info(f"{'='*60}\n")
                return 'discrepancy', reason
            log_info(f"  PASSED: PAFSC skill level is sufficient")
        else:
            log_info(f"  Skipping PAFSC check for {grade}")

        # Final determination
        log_info(f"Step 11: Final Eligibility Determination")
        if btz_check is not None and btz_check is True:
            log_info(f"  ELIGIBLE (BTZ): {member_name} meets all requirements and qualifies for BTZ")
            log_info(f"{'='*60}\n")
            return True, 'btz'
        log_info(f"  ELIGIBLE: {member_name} meets all requirements")
        log_info(f"{'='*60}\n")
        return True
    except Exception as e:
        error_msg = f'Processing error: {str(e)}'
        log_error(f"  EXCEPTION: {error_msg}", exc_info=True)
        log_info(f"{'='*60}\n")
        return False, error_msg