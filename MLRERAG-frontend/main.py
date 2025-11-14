import streamlit as st

from handlers import response_request, get_user_chats, change_chat_handler, reset_current_chat
from schemas import Chat, Message

if not "refresh_token" in st.session_state or not st.session_state["refresh_token"] != "":
    st.switch_page("pages/1_login.py")

if not "access_token" in st.session_state or not st.session_state["access_token"] != "":
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
    """, unsafe_allow_html=True
)


if "chats" not in st.session_state:
    st.session_state["chats"] = {
        "total": 0,
        "page": 0,
        "chats": []
    }
    get_user_chats(0)

if "current_chut" not in st.session_state:
    st.session_state["current_chat"] = Chat(id=None, name=None)

if "messages" not in st.session_state:
    st.session_state["messages"] = [Message(is_users=True, content="a"), Message(is_users=False, content="b")]

st.set_page_config(page_title="MLRERAG")
st.title("MLRERAG")


with st.sidebar:
    st.header("Chats")

    st.button(
        "New Chat",
        use_container_width=True,
        on_click=reset_current_chat
    )
    st.markdown("---")

    for chat in st.session_state["chats"]["chats"]:
        st.button(
            label=f"{chat.name}",
            use_container_width=True,
            key=chat["id"],
            on_click=lambda: change_chat_handler(chat["id"])
        )

    if st.session_state["chats"]["total"] != len(st.session_state["chats"]["chats"]):
        st.button(
            label="Load more",
            use_container_width=True,
            type="tertiary",
            on_click=lambda: get_user_chats(st.session_state["chats"]["page"]))


for message in st.session_state["messages"]:
    if message:
        with st.chat_message("user" if message.is_users else "assistant"):
            st.markdown(message.content)


if prompt := st.chat_input("Спросите что-нибудь..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    assistant_response = response_request(prompt, st.session_state["current_chat"].id)

    with st.chat_message("assistant"):
        st.markdown(assistant_response["answer"])

    st.session_state.messages.append({"role": "assistant", "content": assistant_response["answer"]})