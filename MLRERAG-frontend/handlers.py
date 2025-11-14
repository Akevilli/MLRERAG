import requests
import streamlit as st

from schemas import settings, Chat, Message


def login_handler():
    response = requests.post(
        f"{settings.API_URL}/auth/login",
        json={
            "login": st.session_state["login_form_login"],
            "password": st.session_state["login_form_password"]
        },
    )

    response_data = response.json()

    if response.status_code == 404:
        st.error(response_data["error"]["message"])
        return

    if response.status_code != 200:
        st.json(response_data)
        return

    st.session_state["logged_in"] = True
    st.session_state["access_token"] = response_data["access_token"]
    st.session_state["refresh_token"] = response_data["refresh_token"]
    st.session_state["user_id"] = response_data["id"]

    return


def registration_handler():

    if st.session_state["registration_form_password"] != st.session_state["registration_form_confirm_password"]:
        st.warning("Password and Confirm password do not match!")
        return

    response = requests.post(
        f"{settings.API_URL}/auth/register",
        json={
            "username": st.session_state["registration_form_username"],
            "email": st.session_state["registration_form_email"],
            "password": st.session_state["registration_form_password"],
            "confirm_password": st.session_state["registration_form_confirm_password"]
        },
    )

    response_data = response.json()

    if response.status_code == 409 | response.status_code == 400:
        st.error(response_data["error"]["message"])
        return


    if response.status_code != 201:
        st.error("Unexpected error occurred!")
        return

    st.session_state["registration_success"] = True


def activation_handler():
    response = requests.post(
        f"{settings.API_URL}/auth/activate",
        json={
            "login": st.session_state["activation_form_login"],
            "activation_token": st.session_state["activation_form_token"],
        }
    )

    response_data = response.json()

    if response.status_code == 404 or response.status_code == 400:
        st.error(response_data["error"]["message"])
        return

    if response.status_code != 200:
        st.error("Unexpected error occurred!")
        return

    st.session_state["activation_success"] = True


def reset_current_chat():
    st.session_state["current_chat"] = Chat()
    st.session_state["messages"] = []


def change_chat_handler(chat_id: str):
    load_messages(chat_id)


def get_user_chats(page: int):
    response = requests.get(
        f"{settings.API_URL}/user/me/chats",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {st.session_state['access_token']}"
        },
        params={
            "page": page,
        }
    )

    response_data = response.json()

    if response.status_code != 200:
        st.error(response_data["error"]["message"])
        return

    st.session_state["chats"]["chats"].extend([Chat.model_validate(chat) for chat in response_data["items"]])
    st.session_state["chats"]["page"] += 1
    st.session_state["chats"]["total"] = response_data["total"]


def load_messages(chat_id: str):
    response = requests.get(
        f"{settings.API_URL}/chats/{chat_id}/messages",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {st.session_state['access_token']}"
        },
    )

    response_data = response.json()

    if response.status_code != 200:
        st.error(response_data["error"]["message"])
        return

    st.session_state["messages"] = [Message.model_validate(message) for message in response_data["items"]]


def response_request(prompt: str, chat_id: str | None):
    response = requests.put(
        f"{settings.API_URL}/rag",
        json={
            "prompt": prompt,
            "chat_id": chat_id,
        },
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {st.session_state['access_token']}"
        }
    )

    response_data = response.json()

    if response.status_code != 201:
        st.error(response_data["error"]["message"])

    return response_data