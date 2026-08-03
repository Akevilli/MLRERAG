import streamlit as st

from handlers import (
    generate_response,
    get_user_chats, 
    change_chat_handler, 
    reset_current_chat, 
    upload_pdf_handler
)
from schemas import Chat, Message, PaginatedAPIResponse, PaginationMetadata, PaginationRequest

if not "user" in st.session_state or not st.session_state["user"].refresh_token != "":
    st.switch_page("pages/1_login.py")

if not "user" in st.session_state or not st.session_state["user"].access_token != "":
    st.switch_page("pages/1_login.py")


st.markdown(
    """
    <style>
    button[data-testid="stBaseButton-secondary"] {
        justify-content: start;
        padding-left: 7px;
        border: none;
        background-color: transparent;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if "chats" not in st.session_state:
    st.session_state["chats"] = PaginatedAPIResponse[Chat](
        items=[],
        metadata=PaginationMetadata(
            total=0,
            next=None,
            previous=None,
        )
    )
    get_user_chats(PaginationRequest(page=0, page_size=10, sort="desc"))


if "current_chat" not in st.session_state:
    st.session_state["current_chat"] = Chat(id=None, title=None)


if "messages" not in st.session_state:
    st.session_state["messages"] = PaginatedAPIResponse[Message](
        items=[],
        metadata=PaginationMetadata(
            total=0,
            next=None,
            previous=None,
        )
    )


@st.dialog("Upload PDF Documents")
def open_upload_dialog():
    """Модальное окно с формой."""
    st.write("Select PDF documents to parse and index into the system.")
    
    with st.form("pdf_upload_form", clear_on_submit=True):
        st.file_uploader(
            "Choose PDF files",
            type=["pdf"],
            accept_multiple_files=True,
            key="pdf_uploader_input"
        )
        
        submitted = st.form_submit_button(
            "Upload & Process",
            type="primary",
            on_click=upload_pdf_handler 
        )

st.set_page_config(page_title="MLRERAG")
st.title("MLRERAG")

with st.sidebar:
    st.header("Chats")

    st.button(
        "New Chat",
        use_container_width=True,
        on_click=reset_current_chat,
        type="tertiary"
    )

    st.button(
        "Upload PDFs", 
        use_container_width=True,
        on_click=open_upload_dialog, 
        key="upload_pdf_btn",
        type="tertiary"
    )

    st.markdown("---")

    for chat in st.session_state["chats"].items:
        st.button(
            label=f"{chat.title}" if len(chat.title) < 23 else f"{chat.title[:23]}...",
            use_container_width=True,
            key=chat.id,
            on_click=lambda c_id=chat.id: change_chat_handler(c_id)
        )

    if st.session_state["chats"].metadata.next is not None:
        st.button(
            label="Load more",
            use_container_width=True,
            type="tertiary",
            on_click=lambda: get_user_chats(st.session_state["chats"].metadata.next)
        )


for message in st.session_state["messages"].items:
    if message:
        if message.type == "tool":
            with st.expander("Retrieved documents"):
                st.markdown(message.text)
        else:
            with st.chat_message(message.type):
                st.markdown(message.text)


if prompt := st.chat_input("Спросите что-нибудь..."):
    st.session_state.messages.items.append(Message(type="user", text=prompt))

    with st.chat_message("user"):
        st.markdown(prompt)

    assistant_response = generate_response(prompt, st.session_state["current_chat"].id)

    tool_calls = [message for message in assistant_response.messages if message.type == "tool"]
    assistant_message = assistant_response.messages[-1]

    if tool_calls:
        with st.expander("Retrieved documents"):
            st.markdown("\n\n".join([tool_call.text for tool_call in tool_calls]))

    with st.chat_message("assistant"):
        st.markdown(assistant_message.text)

    st.session_state.messages.items.append(
        Message(
            type="assistant",
            text=assistant_message.text,
        )
    )