"""
Prompt parsing utilities for extracting structured data from natural language prompts
"""

import re
from datetime import datetime, date
from typing import Dict, Optional, List


class PromptParser:
    """Extract structured information from natural language prompts"""

    @staticmethod
    def parse_date(date_str: str) -> Optional[str]:
        """
        Parse various date formats and return as ISO string

        Supported formats:
        - 15 Jan 2025
        - 01/15/2025
        - 2025-01-15
        - January 15, 2025

        Returns:
            ISO format date string (YYYY-MM-DD) or None
        """
        date_patterns = [
            (r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})', '%d %b %Y'),
            (r'(\d{1,2})/(\d{1,2})/(\d{4})', '%m/%d/%Y'),
            (r'(\d{4})-(\d{2})-(\d{2})', '%Y-%m-%d'),
            (r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})', '%B %d %Y')
        ]

        for pattern, fmt in date_patterns:
            match = re.search(pattern, date_str, re.IGNORECASE)
            if match:
                try:
                    # Handle different group structures
                    if len(match.groups()) == 3:
                        date_string = ' '.join(match.groups())
                    else:
                        date_string = match.group(0)

                    parsed_date = datetime.strptime(date_string, fmt)
                    # Return ISO format string for JSON serialization
                    return parsed_date.date().isoformat()
                except ValueError:
                    continue

        return None

    @staticmethod
    def extract_rank_and_name(text: str) -> List[tuple]:
        """
        Extract rank and name pairs from text
        Returns list of (rank, name) tuples

        Example: "MSgt Smith" -> [("MSgt", "Smith")]
        """
        from constants import AF_ENLISTED_RANK_ABBR, AF_OFFICER_RANK_ABBR

        all_ranks = AF_ENLISTED_RANK_ABBR + AF_OFFICER_RANK_ABBR
        rank_pattern = '|'.join(re.escape(rank) for rank in all_ranks)

        # Pattern: Rank followed by capitalized name
        pattern = rf'\b({rank_pattern})\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'

        matches = re.findall(pattern, text)
        return matches

    @staticmethod
    def extract_afi_citations(text: str) -> List[str]:
        """
        Extract AFI citations from text

        Example: "AFI 36-2618, para 3.1" -> ["AFI 36-2618, para 3.1"]
        """
        pattern = r'AFI\s+\d{2}-\d{3,4}(?:,?\s+(?:para|paragraph)\s+[\d.]+)?'
        citations = re.findall(pattern, text, re.IGNORECASE)
        return citations

    @staticmethod
    def extract_subject(prompt: str, document_type: str) -> Optional[str]:
        """Extract subject line from prompt"""

        # Common patterns for subject extraction
        patterns = [
            r'(?:subject|re):\s*(.+?)(?:\.|$)',
            r'(?:about|regarding|concerning)\s+(.+?)(?:\.|on|$)',
            r'documenting\s+(.+?)(?:\.|on|$)'
        ]

        for pattern in patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # If no explicit subject found, generate based on document type
        if document_type == 'mfr':
            # Try to extract event description
            event_match = re.search(r'(?:phone call|meeting|conversation|discussion|briefing)\s+(?:with|about)\s+(.+?)(?:\.|on|$)', prompt, re.IGNORECASE)
            if event_match:
                return f"Documentation of {event_match.group(0).strip()}"

        return None

    def parse_mfr_prompt(self, prompt: str) -> Dict:
        """Parse MFR-specific prompt"""
        extracted = {}

        # Extract subject
        subject = self.extract_subject(prompt, 'mfr')
        if subject:
            extracted['subject'] = subject

        # Extract dates
        dates = re.findall(r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}', prompt, re.IGNORECASE)
        if dates:
            extracted['date'] = self.parse_date(dates[0])

        # Extract participants
        participants = self.extract_rank_and_name(prompt)
        if participants:
            extracted['participants'] = [f"{rank} {name}" for rank, name in participants]

        # Extract body content (everything that looks like a sentence)
        sentences = re.findall(r'[A-Z][^.!?]*[.!?]', prompt)
        if sentences:
            extracted['body_hints'] = sentences

        return extracted

    def parse_appointment_prompt(self, prompt: str) -> Dict:
        """Parse appointment letter-specific prompt"""
        extracted = {}

        # Extract appointee
        appointees = self.extract_rank_and_name(prompt)
        if appointees:
            extracted['appointee_rank'], extracted['appointee_name'] = appointees[0]

        # Extract position title
        position_patterns = [
            r'(?:appoint|designate|assign)(?:ed)?\s+(?:as|to be)\s+(?:the\s+)?(.+?)(?:\.|,|for)',
            r'position(?:\s+of)?:\s*(.+?)(?:\.|,|$)'
        ]
        for pattern in position_patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                extracted['position_title'] = match.group(1).strip()
                break

        # Extract AFI citations
        afis = self.extract_afi_citations(prompt)
        if afis:
            extracted['authority_citation'] = afis[0]

        # Extract effective date
        dates = re.findall(r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}', prompt, re.IGNORECASE)
        if dates:
            extracted['effective_date'] = self.parse_date(dates[0])

        # Extract duties (sentences starting with action verbs)
        duty_verbs = ['conduct', 'maintain', 'ensure', 'coordinate', 'manage', 'supervise', 'perform', 'provide', 'develop']
        duties = []
        for sentence in re.findall(r'[A-Z][^.!?]*[.!?]', prompt):
            for verb in duty_verbs:
                if sentence.lower().startswith(verb):
                    duties.append(sentence.strip())
                    break
        if duties:
            extracted['duties'] = duties

        return extracted

    def parse_administrative_action_prompt(self, prompt: str, action_type: str) -> Dict:
        """Parse LOC/LOA/LOR-specific prompt"""
        extracted = {}

        # Extract member info
        members = self.extract_rank_and_name(prompt)
        if members:
            extracted['member_rank'], extracted['member_name'] = members[0]

        # Extract incident date
        dates = re.findall(r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}', prompt, re.IGNORECASE)
        if dates:
            extracted['incident_date'] = self.parse_date(dates[0])

        # Extract incident description
        incident_patterns = [
            r'(?:was|were)\s+(.+?)(?:\.|on)',
            r'failed to\s+(.+?)(?:\.|$)',
            r'violation of\s+(.+?)(?:\.|$)'
        ]
        for pattern in incident_patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                extracted['incident_description'] = match.group(1).strip()
                break

        # Extract AFI violations
        afis = self.extract_afi_citations(prompt)
        if afis:
            extracted['violations'] = afis

        # Extract previous actions (for LOA/LOR)
        if action_type in ['loa', 'lor']:
            previous_pattern = r'previously\s+(?:counseled|warned|advised)(?:\s+on)?\s+(.+?)(?:\.|$)'
            prev_match = re.search(previous_pattern, prompt, re.IGNORECASE)
            if prev_match:
                extracted['previous_actions'] = [prev_match.group(1).strip()]

        return extracted

    def parse_prompt(self, prompt: str, document_type: str) -> Dict:
        """
        Main parsing method - routes to appropriate parser based on document type

        Args:
            prompt: Natural language prompt
            document_type: One of 'mfr', 'memo', 'appointment', 'loc', 'loa', 'lor'

        Returns:
            Dictionary of extracted fields
        """
        if document_type == 'mfr':
            return self.parse_mfr_prompt(prompt)
        elif document_type == 'memo':
            return self.parse_mfr_prompt(prompt)  # Similar to MFR
        elif document_type == 'appointment':
            return self.parse_appointment_prompt(prompt)
        elif document_type in ['loc', 'loa', 'lor']:
            return self.parse_administrative_action_prompt(prompt, document_type)
        else:
            return {}
