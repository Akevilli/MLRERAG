from datetime import datetime, timezone

import requests
import streamlit as st
import jwt

from schemas import *


def check_jwt():
    encoded_jwt_token = st.session_state["user"].access_token
    payload = jwt.decode(encoded_jwt_token, options={"verify_signature": False})

    if (payload["exp"] - 20 < datetime.now(timezone.utc).timestamp() and
        st.session_state["user"].refresh_token):
        response = requests.post(
            f"{settings.API_URL}/auth/refresh",
            json={
                "user_id": st.session_state["user"].id,
                "refresh_token": st.session_state["user"].refresh_token
            }
        )

        response_data = TokensSchema.model_validate(response.json())

        if response.status_code != 201:
            del st.session_state["user"]
            st.switch_page("pages/1_login.py")

        st.session_state["user"].access_token = response_data.access_token
        st.session_state["user"].refresh_token = response_data.refresh_token


session = requests.Session()


def login(login_str: str, password: str) -> Response[User]:
    response = requests.post(
        f"{settings.API_URL}/api/auth/login",
        json={
            "login": login_str,
            "password": password,
        },
    )

    response_data = response.json()

    if response.status_code == 403:
        st.switch_page("pages/2_activation.py")

    if response.status_code != 200:
        message = response_data.get("error", {}).get("message")
        return Response.fail(message=message if message else "Unexpected error!")

    return Response.success(User.model_validate(response_data))


def registration(
    username: str,
    email: str,
    password: str,
    confirm_password: str,
) -> Response[None]:
    response = requests.post(
        f"{settings.API_URL}/api/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
            "confirm_password": confirm_password
        },
    )

    response_data = response.json()

    if response.status_code != 201:
        message = response_data.get("error", {}).get("message")
        return Response.fail(message=message if message else "Unexpected error!")

    return Response.success(None)


def activation(login_str: str, token: str) -> Response[None]:
    response = requests.post(
        f"{settings.API_URL}/api/auth/activate",
        json={
            "login": login_str,
            "activation_token": token,
        }
    )

    response_data = response.json()

    if response.status_code != 200:
        message = response_data.get("error", {}).get("message")
        return Response.fail(message=message if message else "Unexpected error!")

    return Response.success(None)


def get_chat_by_id(chat_id: str) -> Response[Chat]:
    check_jwt()
    response = session.get(
        f"{settings.API_URL}/api/chats/{chat_id}",
        headers={
            "Authorization": f"Bearer {st.session_state['user'].access_token}",
        }
    )

    response_data = response.json()

    if response.status_code != 200:
        message = response_data.get("error", {}).get("message")
        return Response.fail(message=message if message else "Unexpected error!")

    return Response.success(Chat.model_validate(response_data))


def get_latest_messages(chat_id: str) -> Response[PaginatedAPIResponse[Message]]:
    check_jwt()
    response = session.get(
        f"{settings.API_URL}/api/messages/chats/{chat_id}",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {st.session_state['user'].access_token}"
        },
    )

    response_data = response.json()

    if response.status_code != 200:
        message = response_data.get("error", {}).get("message")
        return Response.fail(message=message if message else "Unexpected error!")

    return Response.success(
        data=PaginatedAPIResponse[Message].model_validate(response_data)
    )


def get_users_chats(page: int) -> Response[PaginatedAPIResponse[Chat]]:
    check_jwt()
    response = session.get(
        f"{settings.API_URL}/api/chats/me",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {st.session_state['user'].access_token}",
        },
        params={
            "page": page,
        }
    )

    response_data = response.json()

    if response.status_code != 200:
        message = response_data.get("error", {}).get("message")
        return Response.fail(message=message if message else "Unexpected error!")

    return Response.success(
        data=PaginatedAPIResponse[Chat].model_validate(response_data)
    )


def generate_answer(prompt: str, chat_id: str | None) -> Response[GeneratedResponse]:
    check_jwt()
    response = session.put(
        f"{settings.API_URL}/api/rag",
        json={
            "prompt": prompt,
            "chat_id": chat_id,
        },
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {st.session_state['user'].access_token}"
        }
    )

    response_data = response.json()

    if response.status_code != 201:
        message = response_data.get("error", {}).get("message")
        return Response.fail(message=message if message else "Unexpected error!")

    return Response.success(GeneratedResponse.model_validate(response_data))