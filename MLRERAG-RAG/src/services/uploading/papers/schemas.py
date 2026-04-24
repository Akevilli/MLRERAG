from typing import Literal, Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PaperRecordBaseDTO(BaseModel):
    """Base DTO for paper record data.

    Contains the core identifiers for a paper record.
    """

    arxiv_id: str
    version: str


class PaperRecordReadDTO(PaperRecordBaseDTO):
    """DTO for reading paper records from the database.

    Includes database-generated fields like ID and timestamps.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    load_status: Literal["in_progress", "completed"]
    created_at: datetime


class PaperRecordCreateDTO(PaperRecordBaseDTO):
    """DTO for creating new paper records.

    Defaults to 'in_progress' status for new records.
    """

    load_status: Literal["in_progress", "completed"] = "in_progress"


class PaperRecordUpdateDTO(BaseModel):
    """DTO for updating existing paper records.

    All fields are optional to support partial updates.
    """
    version: Optional[str] = None
    load_status: Optional[Literal["in_progress", "completed"]] = None