from sqlalchemy.orm import Session

from src.repositories.DocumentRepository import DocumentRepository
from src.services import parsers
from src import models


class DocumentService:
    def __init__(self, repository: DocumentRepository):
        self.repository = repository

    def create(
        self,
        new_documents: list[parsers.Document],
        session: Session
    ) -> None:
        documents = [models.Document(**document.model_dump()) for document in new_documents]
        self.repository.create(documents, session)

    def get_unstored_documents(self, id_list: list[str], session: Session) -> list[str]:
        saved_documents: list[models.Document] =  self.repository.get_by_id(id_list, session)
        saved_documents_ids = [document.id for document in saved_documents]
        unsaved_documents = []

        for id in id_list:
            if id not in saved_documents_ids:
                unsaved_documents.append(id)

        return unsaved_documents



