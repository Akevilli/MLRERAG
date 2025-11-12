import requests
import streamlit as st


def response_request(prompt: str):
    response = requests.put(
        f"http://localhost:8000/api/rag",
        json={
            "prompt": prompt,
            "chat_id": None
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



def login_handler():
    response = requests.post(
        f"http://localhost:8000/api/auth/login",
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
        "http://localhost:8000/api/auth/register",
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
        "http://localhost:8000/api/auth/activate",
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
