from src.shared.schemas import ArxivMetadata
from .schemas import PaperRecordCreateDTO


def arxiv_metadata_to_paper_record_create_dto(arxiv_metadata: ArxivMetadata) -> PaperRecordCreateDTO:
    """Converts ArxivMetadata to a PaperRecordCreateDTO.

    Args:
        arxiv_metadata: An ArxivMetadata instance from an external source.

    Returns:
        A PaperRecordCreateDTO ready for database insertion.
    """
    return PaperRecordCreateDTO(arxiv_id=arxiv_metadata.arxiv_id, version=arxiv_metadata.version)