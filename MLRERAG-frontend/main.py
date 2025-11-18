import streamlit as st

from handlers import generate_response, get_user_chats, change_chat_handler, reset_current_chat
from schemas import Chat, Message, PaginatedAPIResponse


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
        page=0,
        total=0
    )
    get_user_chats(st.session_state["chats"].page)


if "current_chat" not in st.session_state:
    st.session_state["current_chat"] = Chat(id=None, title=None)


if "messages" not in st.session_state:
    st.session_state["messages"] = PaginatedAPIResponse[Message](
        items=[],
        page=0,
        total=0
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

    st.markdown("---")

    for chat in st.session_state["chats"].items:
        st.button(
            label=f"{chat.title}",
            use_container_width=True,
            key=chat.id,
            on_click=lambda c_id=chat.id: change_chat_handler(c_id)
        )

    if st.session_state["chats"].total != len(st.session_state["chats"].items):
        st.button(
            label="Load more",
            use_container_width=True,
            type="tertiary",
            on_click=lambda: get_user_chats(st.session_state["chats"].page + 1)
        )


for message in st.session_state["messages"].items:
    if message:
        with st.chat_message("user" if message.is_users else "assistant"):
            st.markdown(message.content)


if prompt := st.chat_input("Спросите что-нибудь..."):
    st.session_state.messages.items.append(Message(is_users=True, content=prompt))

    with st.chat_message("user"):
        st.markdown(prompt)

    assistant_response = generate_response(prompt, st.session_state["current_chat"].id)

    with st.chat_message("assistant"):
        st.markdown(
            f"# Answer: \n\n {assistant_response.answer} \n\n"
            f"# Documents: \n\n {assistant_response.documents}"
        )

    st.session_state.messages.items.append(
        Message(
            is_users=False,
            content=(
                f"# Answer: \n\n {assistant_response.answer} \n\n"
                f"# Documents: \n\n {assistant_response.documents}"
            )
        )
    )
    st.rerun()