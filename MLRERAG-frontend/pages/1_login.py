import streamlit as st
from handlers import login_handler


st.header("Login")

with st.form("login_form"):
    st.text_input("Username/Email", autocomplete="off", key="login_form_login")
    st.text_input("Password", type="password", key="login_form_password", autocomplete="off")

    st.form_submit_button(
        "Login",
        on_click=login_handler,
        use_container_width=True
    )



if "logged_in" in st.session_state and st.session_state["logged_in"]:
    
    del st.session_state["logged_in"]
    del st.session_state["login_form_login"]
    del st.session_state["login_form_password"]

    st.switch_page("main.py")