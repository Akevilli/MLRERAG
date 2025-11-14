import streamlit as st
from handlers import activation_handler


st.set_page_config(page_title="Email Verification")

st.header("Activation")

with st.form("activation_form"):
    st.text_input("Username/Email", autocomplete="off", key="activation_form_login")
    st.text_input("Token", autocomplete="off", max_chars=8, key="activation_form_token")

    st.form_submit_button(
        "Activate",
        use_container_width=True,
        on_click=activation_handler
    )



if "activation_success" in st.session_state and st.session_state["activation_success"]:
    del st.session_state["activation_success"]
    del st.session_state["activation_form_login"]
    del st.session_state["activation_form_token"]

    st.switch_page("pages/1_login.py")