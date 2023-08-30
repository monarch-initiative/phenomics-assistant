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
    elif message.role == "assistant":
        if message.content:
            with st.chat_message("assistant"):
                st.write(message.content)
        if message.is_function_call and st.session_state.show_function_calls:
            with st.chat_message("assistant", avatar="⚙️"):
                st.write(f"Calling function: `{message.func_name}(params = {message.func_arguments})`")
    elif message.role == "function" and st.session_state.show_function_calls:
        with st.chat_message("assistant", avatar="⚙️"):
            st.write(f"Result: `{message.content}`")

# Handle chat input and responses
def handle_chat_input():
    if prompt := st.chat_input(disabled = st.session_state.ui_disabled):
        agent = st.session_state.agents[st.session_state.current_agent_name]


        # Continue with conversation
        if not agent.get('conversation_started', False):
            messages = agent['agent'].new_chat(prompt, yield_prompt_message=True)
            agent['conversation_started'] = True
        else:
            messages = agent['agent'].continue_chat(prompt, yield_prompt_message=True)

        for message in messages:
           agent['messages'].append(message)
           render_message(message)


# Main Streamlit UI
def main():
    with st.sidebar:
        st.title("Settings")
        agent_names = list(st.session_state.agents.keys())
        current_agent_name = st.selectbox("Base Model", options=agent_names, key="current_agent_name")

        #st.text_input("OpenAI API Key", key="user_api_key", type="password") # not complete
        st.checkbox("Show function calls", key="show_function_calls", disabled = st.session_state.ui_disabled)

    st.title(st.session_state.current_agent_name)

    with st.chat_message("assistant"):
        st.write("Hi, I'm the Monarch Assistant, an AI chatbot!")

    for message in st.session_state.agents[st.session_state.current_agent_name]['messages']:
        render_message(message)

    handle_chat_input()


# Main script execution
if __name__ == "__main__":
    dotenv.load_dotenv()
    initialize_session_state()
    main()
