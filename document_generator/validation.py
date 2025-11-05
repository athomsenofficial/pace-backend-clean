"""
Validation utilities for AF documents
"""

import re
from typing import Tuple, List, Optional
from constants import COMMON_AFIS, AF_ENLISTED_RANK_ABBR, AF_OFFICER_RANK_ABBR


class AFICitationValidator:
    """Validate Air Force Instruction citations"""

    VALID_AFI_PATTERN = r'^AFI\s+\d{2}-\d{3,4}(?:,?\s+(?:para|paragraph)\s+[\d.]+)?$'

    @staticmethod
    def validate_citation(citation: str) -> Tuple[bool, str]:
        """
        Validate AFI citation format

        Args:
            citation: AFI citation string

        Returns:
            (is_valid, message) tuple
        """
        if not citation:
            return False, "AFI citation cannot be empty"

        # Check format
        if not re.match(AFICitationValidator.VALID_AFI_PATTERN, citation.strip(), re.IGNORECASE):
            return False, "AFI citations should follow format: AFI XX-XXXX, para X.X"

        return True, "Valid AFI citation format"

    @staticmethod
    def suggest_afi(topic: str) -> List[str]:
        """
        Suggest relevant AFIs based on topic keywords

        Args:
            topic: Topic or keyword to search

        Returns:
            List of relevant AFI citations with titles
        """
        suggestions = []
        topic_lower = topic.lower()

        for afi, title in COMMON_AFIS.items():
            if topic_lower in title.lower():
                suggestions.append(f"{afi}: {title}")

        return suggestions

    @staticmethod
    def is_known_afi(afi_number: str) -> Tuple[bool, Optional[str]]:
        """
        Check if AFI is in the known list

        Args:
            afi_number: AFI number (e.g., "AFI 36-2618")

        Returns:
            (is_known, title) tuple
        """
        afi_upper = afi_number.upper().strip()

        for known_afi, title in COMMON_AFIS.items():
            if known_afi == afi_upper or afi_upper.startswith(known_afi):
                return True, title

        return False, None


class RankValidator:
    """Validate and format military rank abbreviations"""

    @staticmethod
    def is_valid_rank(rank: str) -> bool:
        """Check if rank abbreviation is valid"""
        return rank in AF_ENLISTED_RANK_ABBR or rank in AF_OFFICER_RANK_ABBR

    @staticmethod
    def is_enlisted(rank: str) -> bool:
        """Check if rank is enlisted"""
        return rank in AF_ENLISTED_RANK_ABBR

    @staticmethod
    def is_officer(rank: str) -> bool:
        """Check if rank is officer"""
        return rank in AF_OFFICER_RANK_ABBR

    @staticmethod
    def format_for_signature(rank: str, name: str) -> str:
        """
        Format name and rank for signature block per T&Q standards

        Args:
            rank: Rank abbreviation
            name: Full name

        Returns:
            Formatted signature line (e.g., "JOHN A. DOE, Capt, USAF")
        """
        return f"{name.upper()}, {rank}, USAF"

    @staticmethod
    def get_full_rank_name(rank_abbr: str) -> Optional[str]:
        """
        Get full rank name from abbreviation

        Args:
            rank_abbr: Rank abbreviation (e.g., "SSgt")

        Returns:
            Full rank name (e.g., "Staff Sergeant") or None if not found
        """
        rank_map = {
            # Enlisted
            'AB': 'Airman Basic',
            'Amn': 'Airman',
            'A1C': 'Airman First Class',
            'SrA': 'Senior Airman',
            'SSgt': 'Staff Sergeant',
            'TSgt': 'Technical Sergeant',
            'MSgt': 'Master Sergeant',
            'SMSgt': 'Senior Master Sergeant',
            'CMSgt': 'Chief Master Sergeant',

            # Officer
            '2d Lt': 'Second Lieutenant',
            '1st Lt': 'First Lieutenant',
            'Capt': 'Captain',
            'Maj': 'Major',
            'Lt Col': 'Lieutenant Colonel',
            'Col': 'Colonel',
            'Brig Gen': 'Brigadier General',
            'Maj Gen': 'Major General',
            'Lt Gen': 'Lieutenant General',
            'Gen': 'General'
        }

        return rank_map.get(rank_abbr)


class DocumentValidator:
    """Validate complete document content"""

    @staticmethod
    def validate_mfr(content: dict) -> Tuple[bool, List[str]]:
        """Validate MFR content"""
        errors = []

        if not content.get('subject'):
            errors.append("Subject line is required")

        if not content.get('body_paragraphs') or len(content.get('body_paragraphs', [])) == 0:
            errors.append("At least one body paragraph is required")

        return len(errors) == 0, errors

    @staticmethod
    def validate_appointment(content: dict) -> Tuple[bool, List[str]]:
        """Validate appointment letter content"""
        errors = []

        required_fields = ['appointee_name', 'appointee_rank', 'position_title',
                          'authority_citation', 'duties', 'effective_date']

        for field in required_fields:
            if not content.get(field):
                errors.append(f"{field.replace('_', ' ').title()} is required")

        # Validate AFI citation if provided
        if content.get('authority_citation'):
            is_valid, msg = AFICitationValidator.validate_citation(content['authority_citation'])
            if not is_valid:
                errors.append(f"Authority citation: {msg}")

        # Validate rank if provided
        if content.get('appointee_rank'):
            if not RankValidator.is_valid_rank(content['appointee_rank']):
                errors.append(f"Invalid rank abbreviation: {content['appointee_rank']}")

        # Validate duties is a list
        if content.get('duties') and not isinstance(content.get('duties'), list):
            errors.append("Duties must be a list of strings")

        return len(errors) == 0, errors

    @staticmethod
    def validate_administrative_action(content: dict, action_type: str) -> Tuple[bool, List[str]]:
        """Validate LOC/LOA/LOR content"""
        errors = []

        required_fields = ['member_name', 'member_rank', 'member_unit', 'subject',
                          'incident_date', 'incident_description', 'violations',
                          'standards_expected', 'consequences']

        for field in required_fields:
            if not content.get(field):
                errors.append(f"{field.replace('_', ' ').title()} is required")

        # Validate rank if provided
        if content.get('member_rank'):
            if not RankValidator.is_valid_rank(content['member_rank']):
                errors.append(f"Invalid rank abbreviation: {content['member_rank']}")

        # Validate violations is a list and contains valid AFIs
        if content.get('violations'):
            if not isinstance(content.get('violations'), list):
                errors.append("Violations must be a list of AFI citations")
            else:
                for violation in content['violations']:
                    is_valid, msg = AFICitationValidator.validate_citation(violation)
                    if not is_valid:
                        errors.append(f"Violation citation '{violation}': {msg}")

        # LOR-specific validation
        if action_type == 'lor':
            if not content.get('filing_location'):
                errors.append("Filing location (PIF/DCAF/UPRG) is required for LOR")

        return len(errors) == 0, errors
