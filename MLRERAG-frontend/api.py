import requests
from schemas import *


def login(login_str: str, password: str) -> Response[User]:
    response = requests.post(
        f"{settings.API_URL}/auth/login",
        json={
            "login": login_str,
            "password": password,
        },
    )

    response_data = response.json()

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
        f"{settings.API_URL}/auth/register",
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
        f"{settings.API_URL}/auth/activate",
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


def get_chat_by_id(chat_id: str, access_token: str) -> Response[Chat]:
    response = requests.get(
        f"{settings.API_URL}/chats/{chat_id}",
        headers={
            "Authorization": f"Bearer {access_token}",
        }
    )

    response_data = response.json()

    if response.status_code != 200:
        message = response_data.get("error", {}).get("message")
        return Response.fail(message=message if message else "Unexpected error!")

    return Response.success(Chat.model_validate(response_data))


def get_latest_messages(chat_id: str, access_token: str) -> Response[PaginatedAPIResponse[Message]]:
    response = requests.get(
        f"{settings.API_URL}/messages/chats/{chat_id}",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        },
    )

    response_data = response.json()

    if response.status_code != 200:
        message = response_data.get("error", {}).get("message")
        return Response.fail(message=message if message else "Unexpected error!")

    return Response.success(
        data=PaginatedAPIResponse[Message].model_validate(response_data)
    )


def get_users_chats(page: int, access_token: str) -> Response[PaginatedAPIResponse[Chat]]:
    response = requests.get(
        f"{settings.API_URL}/chats/me",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
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


def generate_answer(prompt: str, chat_id: str | None, access_token: str) -> Response[GeneratedResponse]:
    response = requests.put(
        f"{settings.API_URL}/rag",
        json={
            "prompt": prompt,
            "chat_id": chat_id,
        },
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
    )

    response_data = response.json()

    if response.status_code != 201:
        message = response_data.get("error", {}).get("message")
        return Response.fail(message=message if message else "Unexpected error!")

    return Response.success(GeneratedResponse.model_validate(response_data))