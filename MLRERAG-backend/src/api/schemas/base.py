from typing import Literal

from pydantic import BaseModel, Field

from src.shared.schemas import PaginationRequestDTO


class BasePaginationRequestSchema(BaseModel):
    page: int = Field(description="Page number", ge=0, default=0)
    page_size: int = Field(description="Page size", ge=0, default=10)
    sort: Literal["asc", "desc"] = Field(default="asc", description="Sorting direction")

    def to_dto(self) -> PaginationRequestDTO:
        return PaginationRequestDTO(**self.model_dump())
