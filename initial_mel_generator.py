import pandas as pd
import os
from io import BytesIO
from fastapi.responses import StreamingResponse
from reportlab.platypus import PageBreak
from reportlab.lib.units import inch

from promotion_eligible_counter import get_promotion_eligibility
from session_manager import get_session
from constants import (
    INITIAL_MEL_HEADER_ROW, INITIAL_MEL_INELIGIBLE_HEADER_ROW,
    INITIAL_MEL_TABLE_WIDTHS, INITIAL_MEL_INELIGIBLE_TABLE_WIDTHS,
    images_dir, default_logo, PDF_MARGIN
)
from pdf_templates import PDF_Template, create_table, merge_pdfs

class InitialMELDocument(PDF_Template):
    """Document template for Initial MEL reports, inheriting from the base template."""
    def __init__(self, filename, cycle, melYear=None, **kwargs):
        super().__init__(filename, cycle, melYear, **kwargs)

def generate_pascode_pdf(eligible_data, ineligible_data, discrepancy_data, btz_data, cycle, melYear,
                         pascode, pas_info, output_filename, logo_path):
    """Generate a PDF for a single pascode."""
    try:
        doc = InitialMELDocument(
            output_filename, cycle=cycle, melYear=melYear,
            rightMargin=PDF_MARGIN, leftMargin=PDF_MARGIN,
            topMargin=PDF_MARGIN, bottomMargin=PDF_MARGIN
        )
        doc.logo_path = logo_path
        doc.pas_info = pas_info
        elements = []
        if eligible_data and len(eligible_data) > 0:
            table = create_table(doc, eligible_data, INITIAL_MEL_HEADER_ROW,
                                 INITIAL_MEL_TABLE_WIDTHS, "ELIGIBLE", len(eligible_data))
            elements.append(table)
            elements.append(PageBreak())
        if ineligible_data and len(ineligible_data) > 0:
            table = create_table(doc, ineligible_data, INITIAL_MEL_INELIGIBLE_HEADER_ROW,
                                 INITIAL_MEL_INELIGIBLE_TABLE_WIDTHS, "INELIGIBLE", len(ineligible_data))
            elements.append(table)
            elements.append(PageBreak())
        if discrepancy_data and len(discrepancy_data) > 0:
            table = create_table(doc, discrepancy_data, INITIAL_MEL_INELIGIBLE_HEADER_ROW,
                                 INITIAL_MEL_INELIGIBLE_TABLE_WIDTHS, "DISCREPANCY", len(discrepancy_data))
            elements.append(table)
            elements.append(PageBreak())
        if btz_data and len(btz_data) > 0:
            table = create_table(doc, btz_data, INITIAL_MEL_HEADER_ROW,
                                 INITIAL_MEL_TABLE_WIDTHS, "BELOW THE ZONE", len(btz_data))
            elements.append(table)
            elements.append(PageBreak())
        doc.build(elements)
        return output_filename
    except Exception as e:
        print(f"Error generating PDF for pascode {pascode}: {e}")
        return None

def generate_small_unit_pdf(small_unit_data, senior_rater, cycle, melYear, pas_info, base_filename, logo_path):
    """Generate PDF for small unit data."""
    try:
        small_unit_filename = base_filename.replace('.pdf', '_small_unit.pdf')
        doc = InitialMELDocument(
            small_unit_filename, cycle=cycle, melYear=melYear,
            rightMargin=PDF_MARGIN, leftMargin=PDF_MARGIN,
            topMargin=PDF_MARGIN, bottomMargin=PDF_MARGIN
        )
        srid_list = small_unit_data.values.tolist() if hasattr(small_unit_data, 'values') else small_unit_data
        must_promote, promote_now = get_promotion_eligibility(len(srid_list), cycle)
        doc.pas_info = {
            'srid': senior_rater.get('srid', 'N/A'),
            'fd name': senior_rater.get('senior_rater_name', 'N/A'),
            'rank': senior_rater.get('senior_rater_rank', 'N/A'),
            'title': senior_rater.get('senior_rater_title', 'N/A'),
            'srid mpf': pas_info.get('srid mpf', 'N/A'),
            'mp': must_promote,
            'pn': promote_now
        }
        doc.logo_path = logo_path
        elements = []
        table = create_table(doc, srid_list, INITIAL_MEL_HEADER_ROW,
                             INITIAL_MEL_TABLE_WIDTHS, "SENIOR RATER", len(srid_list))
        elements.append(table)
        doc.build(elements)
        return small_unit_filename
    except Exception as e:
        print(f"Error generating small unit PDF: {e}")
        return None

def generate_roster_pdf(session_id, output_filename, logo_path=None):
    """Generate a military roster PDF from session data."""
    try:
        session = get_session(session_id)
        if not session:
            print(f"Error: Session {session_id} not found or expired")
            return None

        # Safely get data with defaults
        def clean_dataframe(records):
            """Clean dataframe by removing deleted records and internal columns"""
            df = pd.DataFrame.from_records(records) if records else pd.DataFrame()

            # Filter out soft-deleted records
            if 'deleted' in df.columns:
                df = df[df['deleted'] != True]

            # Remove internal delete-related columns AND any UI-only columns
            columns_to_drop = ['deleted', 'deletion_reason', 'member_id',
                              'REENL_ELIG_STATUS', 'UIF_CODE', 'UIF_DISPOSITION_DATE',
                              'GRADE_PERM_PROJ', '2AFSC', '3AFSC', '4AFSC']
            for col in columns_to_drop:
                if col in df.columns:
                    df = df.drop(columns=[col])

            # Ensure only PDF-appropriate columns remain
            # Keep only columns that were originally in the data
            from constants import PDF_COLUMNS
            expected_cols = PDF_COLUMNS + ['REASON', 'SSAN', 'PAFSC']  # Include some extra cols that might be needed

            # Filter to only keep expected columns
            df_cols = df.columns.tolist()
            cols_to_keep = [col for col in df_cols if col in expected_cols or col in ['FULL_NAME', 'GRADE', 'DATE_ARRIVED_STATION', 'DAFSC', 'ASSIGNED_PAS_CLEARTEXT', 'DOR', 'TAFMSD', 'ASSIGNED_PAS', 'REASON']]
            if cols_to_keep:
                df = df[cols_to_keep]

            return df

        eligible_df = clean_dataframe(session.get('eligible_df', []))
        ineligible_df = clean_dataframe(session.get('ineligible_df', []))
        discrepancy_df = clean_dataframe(session.get('discrepancy_df', []))
        btz_df = clean_dataframe(session.get('btz_df', []))
        small_unit_df = clean_dataframe(session.get('small_unit_df', []))
        cycle = session.get('cycle')
        melYear = session.get('year')
        pascode_map = session.get('pascode_map', {})
        senior_rater = session.get('small_unit_sr', {})
        if not logo_path:
            logo_path = os.path.join(images_dir, default_logo)
        eligible_data = eligible_df.values.tolist() if not eligible_df.empty else []
        btz_data = btz_df.values.tolist() if not btz_df.empty else []
        ineligible_columns = ['FULL_NAME', 'GRADE', 'ASSIGNED_PAS', 'DAFSC', 'ASSIGNED_PAS_CLEARTEXT', 'REASON']
        available_columns = [col for col in ineligible_columns if col in ineligible_df.columns]
        available_discrepancy_columns = [col for col in ineligible_columns if col in discrepancy_df.columns]

        ineligible_data = ineligible_df[available_columns].values.tolist() if not ineligible_df.empty else []
        discrepancy_data = discrepancy_df[available_discrepancy_columns].values.tolist() if not discrepancy_df.empty else []


        unique_pascodes = set()
        for row in eligible_data:
            if len(row) > 7:
                unique_pascodes.add(row[7])
        for row in ineligible_data:
            if len(row) > 2:
                unique_pascodes.add(row[2])
        for row in btz_data:
            if len(row) > 7:
                unique_pascodes.add(row[7])
        unique_pascodes = sorted(list(unique_pascodes))
        temp_pdfs = []
        if not unique_pascodes and not small_unit_df.empty and senior_rater:
            small_unit_temp_filename = f"temp_small_unit.pdf"
            # Format commander name for FDID - check both commander_* and senior_rater_* fields
            su_commander_last = senior_rater.get('commander_last_name') or senior_rater.get('senior_rater_last_name', '')
            su_commander_first = senior_rater.get('commander_first_name') or senior_rater.get('senior_rater_first_name', '')
            su_commander_middle = senior_rater.get('commander_middle_name') or senior_rater.get('senior_rater_middle_name', '')

            # If we have first/last names, use them; otherwise fall back to senior_rater_name
            if su_commander_last or su_commander_first:
                su_commander_name = f"{su_commander_last}, {su_commander_first}"
                if su_commander_middle:
                    su_commander_name += f" {su_commander_middle}"
                su_commander_name = su_commander_name.strip().strip(',')
            else:
                su_commander_name = senior_rater.get('senior_rater_name', 'N/A')

            small_unit_pas_info = {
                'fdid': f'{senior_rater.get("srid", "")}',
                'fd name': su_commander_name if su_commander_name else 'N/A',
                'srid': senior_rater.get("srid", "N/A"),
                'srid mpf': senior_rater.get("srid", "")[:2] if senior_rater.get("srid") else 'N/A'
            }
            small_unit_pdf = generate_small_unit_pdf(
                small_unit_df, senior_rater, cycle, melYear, small_unit_pas_info, small_unit_temp_filename, logo_path
            )
            if small_unit_pdf:
                temp_pdfs.append(small_unit_pdf)
            return merge_pdfs(temp_pdfs, session_id)
        for pascode in unique_pascodes:
            if pascode not in pascode_map:
                continue
            pascode_eligible = [row for row in eligible_data if len(row) > 7 and row[7] == pascode]
            pascode_ineligible = [row for row in ineligible_data if len(row) > 2 and row[2] == pascode]
            pascode_discrepancy = [row for row in discrepancy_data if len(row) > 2 and row[2] == pascode]
            pascode_btz = [row for row in btz_data if len(row) > 7 and row[7] == pascode]
            if not pascode_eligible and not pascode_ineligible and not pascode_btz:
                continue
            eligible_candidates = len(pascode_eligible)
            must_promote, promote_now = get_promotion_eligibility(eligible_candidates, cycle)
            # Format commander name for FD Name - check both commander_* and senior_rater_* fields
            commander_last = pascode_map[pascode].get('commander_last_name') or pascode_map[pascode].get('senior_rater_last_name', '')
            commander_first = pascode_map[pascode].get('commander_first_name') or pascode_map[pascode].get('senior_rater_first_name', '')
            commander_middle = pascode_map[pascode].get('commander_middle_name') or pascode_map[pascode].get('senior_rater_middle_name', '')

            # If we have first/last names, use them; otherwise fall back to senior_rater_name
            if commander_last or commander_first:
                commander_name = f"{commander_last}, {commander_first}"
                if commander_middle:
                    commander_name += f" {commander_middle}"
                commander_name = commander_name.strip().strip(',')
            else:
                commander_name = pascode_map[pascode].get('senior_rater_name', 'N/A')

            # For large units, use commander info for signature block
            pas_info = {
                'srid': pascode_map[pascode].get('srid', 'N/A'),
                'rank': pascode_map[pascode].get('commander_rank') or pascode_map[pascode].get('senior_rater_rank', 'N/A'),
                'title': pascode_map[pascode].get('commander_title') or pascode_map[pascode].get('senior_rater_title', 'N/A'),
                'fd name': commander_name,
                'fdid': f'{pascode_map[pascode].get("srid", "")}{pascode[-4:]}',
                'srid mpf': pascode[:2],
                'mp': must_promote,
                'pn': promote_now
            }
            temp_filename = f"temp_{pascode}.pdf"
            temp_pdf = generate_pascode_pdf(
                pascode_eligible,
                pascode_ineligible,
                pascode_discrepancy,
                pascode_btz,
                cycle,
                melYear,
                pascode,
                pas_info,
                temp_filename,
                logo_path
            )
            if temp_pdf:
                temp_pdfs.append(temp_pdf)
        if not small_unit_df.empty and senior_rater:
            small_unit_temp_filename = f"temp_small_unit.pdf"
            # Format commander name for FDID - check both commander_* and senior_rater_* fields
            su_commander_last = senior_rater.get('commander_last_name') or senior_rater.get('senior_rater_last_name', '')
            su_commander_first = senior_rater.get('commander_first_name') or senior_rater.get('senior_rater_first_name', '')
            su_commander_middle = senior_rater.get('commander_middle_name') or senior_rater.get('senior_rater_middle_name', '')

            # If we have first/last names, use them; otherwise fall back to senior_rater_name
            if su_commander_last or su_commander_first:
                su_commander_name = f"{su_commander_last}, {su_commander_first}"
                if su_commander_middle:
                    su_commander_name += f" {su_commander_middle}"
                su_commander_name = su_commander_name.strip().strip(',')
            else:
                su_commander_name = senior_rater.get('senior_rater_name', 'N/A')

            small_unit_pas_info = {
                'fdid': f'{senior_rater.get("srid", "")}',
                'fd name': su_commander_name if su_commander_name else 'N/A',
                'srid': senior_rater.get("srid", "N/A"),
                'srid mpf': senior_rater.get("srid", "")[:2] if senior_rater.get("srid") else 'N/A'
            }
            small_unit_pdf = generate_small_unit_pdf(
                small_unit_df,
                senior_rater,
                cycle,
                melYear,
                small_unit_pas_info,
                small_unit_temp_filename,
                logo_path
            )
            if small_unit_pdf:
                temp_pdfs.append(small_unit_pdf)
        return merge_pdfs(temp_pdfs, session_id)
    except Exception as e:
        print(f"Error generating roster PDF: {e}")
        return None
