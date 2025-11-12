import streamlit as st

from handlers import response_request

st.session_state["chat_disabled"] = False

st.title("MLRERAG")


if not "refresh_token" in st.session_state or not st.session_state["refresh_token"] != "":
    st.switch_page("pages/1_login.py")

with st.sidebar:
    st.header("Chats")

    st.markdown("[New Chat]()")

    for i in range(3):
        st.markdown(f"[Chat {i + 1}](#)")


if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    if message:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("Спросите что-нибудь..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    assistant_response = response_request(prompt)

    with st.chat_message("assistant"):
        st.markdown(assistant_response["answer"])

    st.session_state.messages.append({"role": "assistant", "content": assistant_response["answer"]})