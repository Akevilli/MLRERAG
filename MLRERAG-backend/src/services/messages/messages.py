from uuid import UUID

from src.core import retry_strategy
from src.services.chats import ChatService
from src.shared.schemas import PaginationRequestDTO, PaginationMetadataDTO, PaginationResponseDTO
from src.shared.repositories import MessageRepository
from src.shared.databases.postgres.models import Message
from .schemas import MessageViewDTO, CreateMessageDTO


class MessageService:
    def __init__(
        self,
        message_repository: MessageRepository,
        chat_service: ChatService,
    ):
        self._message_repository = message_repository
        self._chat_service = chat_service

    @staticmethod
    def _get_message_view(message: Message) -> MessageViewDTO:
        return MessageViewDTO(
            id=message.id,
            text=message.text,
            type=message.type,
            chat_id=message.chat_id,
        )

    @retry_strategy
    async def get_chat_messages(
            self,
            chat_id: UUID,
            pagination_request_dto: PaginationRequestDTO,
            user_credentials: dict,
    ) -> PaginationResponseDTO:
        chat = await self._chat_service.get_by_id(chat_id, user_credentials)
        page = pagination_request_dto.page
        page_size = pagination_request_dto.page_size
        sort = pagination_request_dto.sort

        total, messages = await self._message_repository.get_messages_by_chat_id(
            chat_id=chat.id,
            page=page,
            page_size=page_size,
            sort=sort,
        )

        pagination_metadata = PaginationMetadataDTO.create(total, pagination_request_dto)

        return PaginationResponseDTO(
            metadata=pagination_metadata,
            items=[self._get_message_view(message) for message in messages],
        )


    @retry_strategy
    async def create(self, message_schema: CreateMessageDTO) -> MessageViewDTO:
        message = Message(**message_schema.model_dump())
        message = await self._message_repository.create(message)

        return self._get_message_view(message)
