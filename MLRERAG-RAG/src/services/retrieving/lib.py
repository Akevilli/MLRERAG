from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

from src.shared.schemas import Message, MessageType


message_type_to_message_map = {
    MessageType.ASSISTANT: AIMessage,
    MessageType.TOOL: ToolMessage,
    MessageType.SYSTEM: SystemMessage,
    MessageType.USER: HumanMessage
}

message_to_message_type = {
    "ai": MessageType.ASSISTANT,
    "tool": MessageType.TOOL,
    "system": MessageType.SYSTEM,
    "human": MessageType.USER
}

def message_dto_to_message(message_dto: Message) -> SystemMessage | HumanMessage | AIMessage | ToolMessage:
    return message_type_to_message_map[message_dto.type](content=message_dto.text)

def message_to_message_dto(message: SystemMessage | HumanMessage | AIMessage | ToolMessage) -> Message:
    return Message(
        text=f"{message.tool_calls}" if message.type == "ai" and message.tool_calls else message.content,
        type=message_to_message_type[message.type]
    )