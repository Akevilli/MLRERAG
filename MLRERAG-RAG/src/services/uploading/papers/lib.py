from typing import Literal

from src.shared.schemas import ArxivMetadata
from .schemas import PaperRecordCreateDTO, PaperRecordUpdateDTO


def arxiv_metadata_to_paper_record_create_dto(arxiv_metadata: ArxivMetadata) -> PaperRecordCreateDTO:
    """Converts ArxivMetadata to a PaperRecordCreateDTO.

    Args:
        arxiv_metadata: An ArxivMetadata instance from an external source.

    Returns:
        A PaperRecordCreateDTO ready for database insertion.
    """
    return PaperRecordCreateDTO(arxiv_id=arxiv_metadata.arxiv_id, version=arxiv_metadata.version)

def arxiv_metadata_to_paper_record_update_dto(
        arxiv_metadata: ArxivMetadata,
        status: Literal["in_progress", "completed"]
) -> PaperRecordUpdateDTO:
    return PaperRecordUpdateDTO(
        version=arxiv_metadata.version,
        load_status=status,
    )