from api import *


def login_handler():
    response = login(
        st.session_state["login_form_login"],
        st.session_state["login_form_password"]
    )

    if not response.is_success:
        st.error(response.message)
        return

    st.session_state["logged_in"] = True
    st.session_state["user"] = response.data


def registration_handler():
    if st.session_state["registration_form_password"] != st.session_state["registration_form_confirm_password"]:
        st.warning("Password and Confirm password do not match!")
        return

    response = registration(
        st.session_state["registration_form_username"],
        st.session_state["registration_form_email"],
        st.session_state["registration_form_password"],
        st.session_state["registration_form_confirm_password"]
    )

    if not response.is_success:
        st.error(response.message)
        return

    st.session_state["registration_success"] = True


def activation_handler():
    response = activation(
        st.session_state["activation_form_login"],
        st.session_state["activation_form_token"]
    )

    if not response.is_success:
        st.error(response.message)
        return

    st.session_state["activation_success"] = True


def reset_current_chat():
    st.session_state["current_chat"] = Chat()
    st.session_state["messages"] = PaginatedAPIResponse[Message](
        items=[],
        page=0,
        total=0
    )


def change_chat_handler(chat_id: str):
    chat_response = get_chat_by_id(chat_id)

    if not chat_response.is_success:
        st.error(chat_response.message)
        return

    st.session_state["current_chat"] = chat_response.data

    message_response = get_latest_messages(chat_id)

    if not message_response.is_success:
        st.error(message_response.message)
        return

    st.session_state["messages"] = message_response.data


def get_user_chats(page: int):
    response = get_users_chats(page)

    if not response.is_success:
        st.error(response.message)
        return

    st.session_state["chats"] = response.data


def generate_response(prompt: str, chat_id: str | None) -> GeneratedResponse | None:
    response = generate_answer(prompt, chat_id)

    if not response.is_success:
        st.error(response.message)
        return None

    if st.session_state["current_chat"].id is None:
        chat = Chat.model_validate(response.data.chat)
        st.session_state["current_chat"] = chat
        get_user_chats(0)

    return response.data