from datetime import datetime
from dateutil.relativedelta import relativedelta
from constants import SCODS, ACCOUNTING_DATE_OFFSET_DAYS
from typing import Optional
from logging import Logger

def accounting_date_check(
    date_arrived_station: Optional[datetime],
    grade: str,
    year: int,
    logger: Optional[Logger] = None
) -> bool:
    """
    Check if member's Date Arrived Station meets accounting date requirements.

    Args:
        date_arrived_station: Member's DAS
        grade: Current grade
        year: Promotion cycle year (release year)
        logger: Optional logger for detailed output

    Returns:
        bool: True if eligible, False if not
    """
    if not date_arrived_station:
        if logger:
            logger.warning(f"  DAS Check: Missing DAS - FAILED")
        return False

    # Determine SCOD year based on month
    scod_month_day = SCODS.get(grade)
    month_name = scod_month_day.split('-')[1]

    if month_name in ['JAN', 'FEB', 'MAR']:
        scod_year = year + 1
    else:
        scod_year = year

    scod = f'{scod_month_day}-{scod_year}'
    formatted_scod_date = datetime.strptime(scod, "%d-%b-%Y")

    # Calculate accounting date (SCOD - ACCOUNTING_DATE_OFFSET_DAYS, then set to 3rd of month)
    accounting_date = formatted_scod_date - relativedelta(days=ACCOUNTING_DATE_OFFSET_DAYS)
    adjusted_accounting_date = accounting_date.replace(day=3, hour=23, minute=59, second=59)

    if logger:
        logger.info(f"  DAS Check Details:")
        logger.info(f"    SCOD: {formatted_scod_date.strftime('%d-%b-%Y')}")
        logger.info(f"    Accounting Date (SCOD - 119 days): {accounting_date.strftime('%d-%b-%Y')}")
        logger.info(f"    Adjusted Accounting Date (3rd of month): {adjusted_accounting_date.strftime('%d-%b-%Y %H:%M:%S')}")
        logger.info(f"    Member DAS: {date_arrived_station.strftime('%d-%b-%Y')}")

    if date_arrived_station > adjusted_accounting_date:
        if logger:
            logger.warning(f"    Result: FAILED - DAS ({date_arrived_station.strftime('%d-%b-%Y')}) is after accounting date ({adjusted_accounting_date.strftime('%d-%b-%Y')})")
        return False

    if logger:
        logger.info(f"    Result: PASSED - DAS is on or before accounting date")
    return True