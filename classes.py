from typing import Dict
from pydantic import BaseModel

class PasCodeInfo(BaseModel):
    srid: str
    senior_rater_name: str
    senior_rater_rank: str
    senior_rater_title: str
    senior_rater_first_name: str | None = None
    senior_rater_middle_name: str | None = None
    senior_rater_last_name: str | None = None
    commander_rank: str | None = None
    commander_first_name: str | None = None
    commander_middle_name: str | None = None
    commander_last_name: str | None = None

class PasCodeSubmission(BaseModel):
    session_id: str
    pascode_info: Dict[str, PasCodeInfo]
