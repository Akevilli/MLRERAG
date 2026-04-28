from typing import List, Literal, Optional, Any, Self

from pydantic import BaseModel, Field


class PaginationRequestDTO(BaseModel):
    page: int = Field(description="Page number", ge=0, default=0)
    page_size: int = Field(description="Page size", ge=0, default=10)
    sort: Literal["asc", "desc"] = Field(description="Sort order", default="asc")

    def get_previous_page_request(self) -> Self:
        return PaginationRequestDTO(
            page=self.page - 1,
            page_size=self.page_size,
            sort=self.sort,
        )

    def get_next_page_request(self) -> Self:
        return PaginationRequestDTO(
            page=self.page + 1,
            page_size=self.page_size,
            sort=self.sort,
        )


class PaginationMetadataDTO(BaseModel):
    total: int = Field(description="Total items", ge=0)
    next: Optional[PaginationRequestDTO] = Field(description="Url to next page")
    previous: Optional[PaginationRequestDTO] = Field(description="Url to previous page")

    @staticmethod
    def create(total: int, request: PaginationRequestDTO):
        return PaginationMetadataDTO(
            total=total,
            next=request.get_next_page_request() if total - (request.page + 1) * request.page_size > request.page_size else None,
            previous=request.get_previous_page_request() if (request.page - 1) > 0 else None,
        )

class PaginationResponseDTO(BaseModel):
    items: List[Any] = Field(description="List of items")
    metadata: PaginationMetadataDTO = Field(description="Metadata")
