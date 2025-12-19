import streamlit as st
from handlers import registration_handler


st.set_page_config(page_title="Registration")

st.header("Registration")

with st.form("registration_form"):
    st.text_input("Username", autocomplete="off", key="registration_form_username")
    st.text_input("Email", autocomplete="off", key="registration_form_email")
    st.text_input("Password", type="password", key="registration_form_password", autocomplete="off")
    st.text_input("Confirm Password", type="password", key="registration_form_confirm_password", autocomplete="off")

    st.form_submit_button(
        "Sign Up",
        on_click=registration_handler,
        use_container_width=True
    )

with st.container(horizontal=True):
    st.text("Already have an account?")
    st.page_link(page="pages/1_login.py", label="Login")


if "registration_success" in st.session_state and st.session_state["registration_success"]:
    del st.session_state["registration_success"]
    del st.session_state["registration_form_username"]
    del st.session_state["registration_form_email"]
    del st.session_state["registration_form_password"]
    del st.session_state["registration_form_confirm_password"]

    st.switch_page("pages/2_activation.py")
