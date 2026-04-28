from uuid import UUID

from fastapi import HTTPException

from src.core import retry_strategy
from src.shared.schemas import PaginationRequestDTO, PaginationMetadataDTO, PaginationResponseDTO
from src.shared.repositories import ChatRepository
from src.shared.databases.postgres.models import Chat
from .schemas import ChatViewDTO, CreateChatDTO


class ChatService:
    def __init__(
        self,
        chat_repository: ChatRepository
    ):
        self._chat_repository = chat_repository

    @staticmethod
    def _get_chat_view(chat: Chat) -> ChatViewDTO:
        return ChatViewDTO(
            id=chat.id,
            owner_id=chat.owner_id,
            title=chat.title,
        )

    @retry_strategy
    async def get_by_id(self, chat_id: UUID, user_credentials: dict) -> ChatViewDTO:
        chat = await self._chat_repository.get_by_id(chat_id)

        if chat is None:
            raise HTTPException(status_code=404, detail="Chat not found")

        if str(chat.owner_id) != user_credentials['user_id']:
            raise HTTPException(status_code=403, detail="You don't have permission to access this chat.")

        return self._get_chat_view(chat)


    @retry_strategy
    async def get_chats(
            self,
            pagination_request_dto: PaginationRequestDTO,
            user_credentials: dict
    ) -> PaginationResponseDTO:
        page = pagination_request_dto.page
        page_size = pagination_request_dto.page_size
        sort = pagination_request_dto.sort

        total, chats = await self._chat_repository.get_chats(
            page=page,
            page_size=page_size,
            sort=sort,
            user_id=user_credentials["user_id"]
        )
        pagination_metadata = PaginationMetadataDTO.create(total, pagination_request_dto)

        return PaginationResponseDTO(
            metadata=pagination_metadata,
            items=[self._get_chat_view(chat) for chat in chats]
        )


    @retry_strategy
    async def create(self, chat_schema: CreateChatDTO) -> ChatViewDTO:
        chat = Chat(**chat_schema.model_dump())
        chat = await self._chat_repository.create(chat)

        return self._get_chat_view(chat)