from httpx import AsyncClient
from loguru import logger

from src.core import settings, retry_strategy
from src.shared.schemas import PaginationRequestDTO
from src.services.redis import RedisService
from src.services.chats import ChatService, CreateChatDTO
from src.services.messages import MessageService, BaseMessageDTO, CreateMessageDTO
from .schemas import RAGRequestDTO, RAGResponseDTO, RAGRServiceResponseDTO


class RAGService:
    def __init__(
        self,
        httpx_client: AsyncClient,
        chat_service: ChatService,
        message_service: MessageService,
        redis_service: RedisService,
    ):
        self._httpx_client = httpx_client
        self._chat_service = chat_service
        self._message_service = message_service
        self._redis_service = redis_service


    @retry_strategy
    async def generate_answer(
        self,
        request: RAGRequestDTO,
        user_credentials: dict,
    ) -> RAGRServiceResponseDTO | dict:
        is_new_chat = False

        if request.chat_id is None:
            is_new_chat = True
            current_chat = await self._chat_service.create(
                CreateChatDTO(
                    title=" ".join(request.query.split()[:25]),
                    owner_id=user_credentials["user_id"]
                )
            )
        else:
            current_chat = await self._chat_service.get_by_id(request.chat_id, user_credentials)

        messages = []

        if not is_new_chat:
            messages = await self._redis_service.get_messages(current_chat.id)
            if messages is None:
                pagination_request = PaginationRequestDTO(
                    page=0,
                    page_size=settings.CONTEXT_WINDOW,
                    sort="desc"
                )
                messages = (await self._message_service.get_chat_messages(
                    current_chat.id,
                    pagination_request,
                    user_credentials,
                )).items

                messages = [message for message in messages if message.type != "tool"]

                await self._redis_service.append_messages(current_chat.id, messages)

        user_message = BaseMessageDTO(text=request.query, type="user", chat_id=current_chat.id)
        user_message = await self._message_service.create(CreateMessageDTO(**user_message.model_dump()))
        messages.append(user_message)

        response = await self._httpx_client.post(
            url=settings.RAG_SERVICE_URL + "/rag/generate_answer",
            json={"messages": [message.model_dump(exclude={"id", "chat_id"}) for message in messages]},
            timeout=None
        )

        if response.status_code != 200:
            return response.json()

        result = RAGResponseDTO.model_validate(response.json())
        logger.info(f"RAG response: {result}")

        messages = []

        for message_json in result.messages:
            message = await self._message_service.create(
                CreateMessageDTO(
                    text=message_json.text,
                    chat_id=current_chat.id,
                    type=message_json.type
                )
            )

            if message.type != "tool":
                messages.append(message)

        await self._redis_service.append_messages(current_chat.id, [user_message, *messages])

        return RAGRServiceResponseDTO(
            messages=result.messages,
            chat=current_chat
        )

