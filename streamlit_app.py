import streamlit as st
import os
from monarch_agent import MonarchAgent
import dotenv

# Initialize session states
def initialize_session_state():
    st.session_state.setdefault("user_api_key", "")
    st.session_state.setdefault("show_function_calls", False)
    st.session_state.setdefault("openai_api_key", os.environ["OPENAI_API_KEY"])
    st.session_state.setdefault("current_agent_name", "GPT-3.5 16k Agent")
    st.session_state.setdefault("ui_disabled", False)
    st.session_state.setdefault("lock_widgets", False)  # Step 1: Initialize lock_widgets session state

    if "agents" not in st.session_state:
        st.session_state.agents = {
            "GPT-3.5 16k Agent": {
                "agent": MonarchAgent("Monarch Agent", model="gpt-3.5-turbo-16k-0613", openai_api_key=st.session_state.openai_api_key),
            },
            "GPT-4 Agent": {
                "agent": MonarchAgent("Monarch Agent", model="gpt-4-0613", openai_api_key=st.session_state.openai_api_key),
            }
        }

    for agent in st.session_state.agents.values():
        if "conversation_started" not in agent:
            agent["conversation_started"] = False
        if "messages" not in agent:
            agent["messages"] = []

# Render chat message
def render_message(message):
    if message.role == "user":
        with st.chat_message("user"):
            st.write(message.content)
    elif message.role == "system":
        with st.chat_message("assistant", avatar="ℹ️"):
            st.write(message.content)
    elif message.role == "assistant" and not message.is_function_call:
        with st.chat_message("assistant"):
            st.write(message.content)

    if st.session_state.show_function_calls:
        if message.is_function_call:
            with st.chat_message("assistant", avatar="⚙️"):
                st.write(f"Calling function: `{message.func_name}(params = {message.func_arguments})`")

        elif message.role == "function":
            with st.chat_message("assistant", avatar="⚙️"):
                st.write(f"Result: `{message.content}`")
    
    else:
        if message.is_function_call:
            with st.chat_message("assistant"):
                st.write("Please hold, I need to check my sources...")

# Handle chat input and responses
def handle_chat_input():
    if prompt := st.chat_input(disabled=st.session_state.lock_widgets, on_submit=lock_ui):  # Step 4: Add on_submit callback
        agent = st.session_state.agents[st.session_state.current_agent_name]

        # Continue with conversation
        if not agent.get('conversation_started', False):
            messages = agent['agent'].new_chat(prompt, yield_prompt_message=True)
            agent['conversation_started'] = True
        else:
            messages = agent['agent'].continue_chat(prompt, yield_prompt_message=True)

        # for message in messages:
        #     agent['messages'].append(message)
        #     render_message(message)
        while True:
            try:
                with st.spinner("Thinking..."):
                    message = next(messages)
                    agent['messages'].append(message)
                    render_message(message)
            except StopIteration:
                break

        st.session_state.lock_widgets = False  # Step 5: Unlock the UI
        st.experimental_rerun()

# Lock the UI when user submits input
def lock_ui():
    st.session_state.lock_widgets = True

# Main Streamlit UI
def main():
    with st.sidebar:
        st.title("Settings")
        agent_names = list(st.session_state.agents.keys())
        current_agent_name = st.selectbox("Base Model", options=agent_names, key="current_agent_name", disabled=st.session_state.lock_widgets)  # Step 2: Respect lock_widgets
        st.checkbox("Show function calls", key="show_function_calls", disabled=st.session_state.lock_widgets)  # Step 2: Respect lock_widgets

    st.title(st.session_state.current_agent_name)

    with st.chat_message("assistant"):
        st.write("Hi, I'm the Monarch Assistant, an AI chatbot!")

    for message in st.session_state.agents[st.session_state.current_agent_name]['messages']:
        render_message(message)

    handle_chat_input()  # Step 3: Move handle_chat_input to the bottom

# Main script execution
if __name__ == "__main__":
    dotenv.load_dotenv()
    initialize_session_state()
    main()
