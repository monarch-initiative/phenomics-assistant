import streamlit as st
from monarch_agent import MonarchAgent

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

agent = MonarchAgent("Monarch Agent")

st.title("Monarch Agent") 
# if "messages" not in st.session_state:
#     st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

# for msg in st.session_state.messages:
#     st.chat_message(msg["role"]).write(msg["content"])

st.chat_message("assistant").write("How can I help you?")

if prompt := st.chat_input():
    print("hey that tickles")
    # if not openai_api_key: 
    #     st.info("Please add your OpenAI API key to continue.")
    #     st.stop()

    # openai.api_key = openai_api_key
    for message in agent.new_chat(prompt):
        #st.session_state.messages.append(message.model_dump()) # save the message to the session state
        st.chat_message(message.role).write(message.content)