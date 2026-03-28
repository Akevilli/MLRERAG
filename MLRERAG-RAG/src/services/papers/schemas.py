from typing import Literal, Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PaperRecordBaseDTO(BaseModel):
    arxiv_id: str
    version: int


class PaperRecordReadDTO(PaperRecordBaseDTO):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    load_status: Literal["in_progress", "completed"]
    created_at: datetime


class PaperRecordCreateDTO(PaperRecordBaseDTO):
    load_status: Literal["in_progress", "completed"] = "in_progress"


class PaperRecordUpdateDTO(BaseModel):
    version: Optional[int] = None
    load_status: Optional[Literal["in_progress", "completed"]] = None