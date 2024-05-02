import streamlit as st
import os
from agents import PhenomicsAgent
import dotenv
import logging



# Initialize session states
def initialize_session_state():
    if "logger" not in st.session_state:
        st.session_state.logger = logging.getLogger(__name__)
        st.session_state.logger.handlers = []
        st.session_state.logger.setLevel(logging.INFO)
        st.session_state.logger.addHandler(logging.StreamHandler())

    st.session_state.setdefault("user_api_key", "")
    st.session_state.setdefault("original_api_key", os.environ.get("OPENAI_API_KEY", None))  # Store the original API key
    st.session_state.setdefault("show_function_calls", False)
    st.session_state.setdefault("ui_disabled", False)
    st.session_state.setdefault("lock_widgets", False)

    greeting = """I'm the Phenomics Assistant, an AI chatbot with access to the [Monarch Inititive](https://monarchinitiative.org) biomedical knowledgebase. I can search for information on diseases, genes, and phenotypes. Here are some things you might try asking:
    
- What is the genetic basis of Cystic Fibrosis?
- What symptoms are associated with Fanconi Anemia?

Please note that I am a research preview, and this information should not be used for diagnoses, clinical decision making, or other medical applications."""


    if "agents" not in st.session_state:
        st.session_state.agents = {
            "Phenomics Assistant": {
                "agent": PhenomicsAgent("Phenomics Assistant", model="gpt-4-turbo-2024-04-09", openai_api_key=get_current_api_key_for_agent_use()),
                "greeting": greeting,
                "avatar": "ℹ️",
                "user_avatar": "👤",
            },
            "Phenomics Assistant (GPT 3.5)": {
                "agent": PhenomicsAgent("Phenomics Assistant", model="gpt-3.5-turbo-16k-0613", openai_api_key=get_current_api_key_for_agent_use()),
                "greeting": greeting,
                "avatar": "ℹ️",
                "user_avatar": "👤",
            }
        }

    st.session_state.setdefault("current_agent_name", list(st.session_state.agents.keys())[0])

    for agent in st.session_state.agents.values():
        if "conversation_started" not in agent:
            agent["conversation_started"] = False
        if "messages" not in agent:
            agent["messages"] = []

def initialize_page():
    st.set_page_config(
        page_title="Phenomics Assistant",
        page_icon="ℹ️",
        layout="centered",
        initial_sidebar_state="expanded",
        menu_items={
            "Get Help": "https://github.com/monarch-initiative/phenomics-assistant/issues",
            "About": "This application is brought to you in part by the [Monarch Initiative](https://next.monarchinitiative.org).",
        }
    )

# Get the current API key, either the user's or the default
def get_current_api_key_for_agent_use():
    key = st.session_state.user_api_key if st.session_state.user_api_key else st.session_state.original_api_key
    if key is None:
        key = "placeholder"
    return key

# Update agents with new API key
def update_agents_api_key():
    for agent in st.session_state.agents.values():
        agent["agent"].set_api_key(get_current_api_key_for_agent_use())

# Check if we have a valid API key
def has_valid_api_key():
    return bool(st.session_state.user_api_key) or bool(st.session_state.original_api_key)


# Render chat message
def render_message(message):
    current_agent_avatar = st.session_state.agents[st.session_state.current_agent_name].get("avatar", None)
    current_user_avatar = st.session_state.agents[st.session_state.current_agent_name].get("user_avatar", None)

    if message.role == "user":
        with st.chat_message("user", avatar = current_user_avatar):
            st.write(message.content)

    elif message.role == "system":
        with st.chat_message("assistant", avatar="ℹ️"):
            st.write(message.content)

    elif message.role == "assistant" and not message.is_function_call:
        with st.chat_message("assistant", avatar=current_agent_avatar):
            st.write(message.content)

    if st.session_state.show_function_calls:
        if message.is_function_call:
            with st.chat_message("assistant", avatar="🛠️"):
                st.text(f"{message.func_name}(params = {message.func_arguments})")

        elif message.role == "function":
            with st.chat_message("assistant", avatar="✔️"):
                st.text(message.content)

    current_action = "*Thinking...*"

    if message.is_function_call:
        current_action = f"*Checking source ({message.func_name})...*"
    elif message.role == "function":
        current_action = f"*Evaluating result ({message.func_name})...*"

    return current_action
    
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

        st.session_state.current_action = "*Thinking...*"
        while True:
            try:
                with st.spinner(st.session_state.current_action):
                    message = next(messages)
                    agent['messages'].append(message)
                    st.session_state.current_action = render_message(message)
       
                    session_id = st.runtime.scriptrunner.add_script_run_ctx().streamlit_script_run_ctx.session_id
                    info = {"session_id": session_id, "message": message.model_dump(), "agent": st.session_state.current_agent_name}
                    st.session_state.logger.info(info)
            except StopIteration:
                break

        st.session_state.lock_widgets = False  # Step 5: Unlock the UI
        st.experimental_rerun()

def clear_chat_current_agent():
    current_agent = st.session_state.agents[st.session_state.current_agent_name]
    current_agent['conversation_started'] = False
    current_agent['agent'].clear_history()
    st.session_state.agents[st.session_state.current_agent_name]['messages'] = []


# Lock the UI when user submits input
def lock_ui():
    st.session_state.lock_widgets = True

# Main Streamlit UI
def main():
    with st.sidebar:
        # st.title("Settings")

        agent_names = list(st.session_state.agents.keys())
        current_agent_name = st.selectbox(label = "**Assistant**", 
                                          options=agent_names, 
                                          key="current_agent_name", 
                                          disabled=st.session_state.lock_widgets, 
                                          label_visibility="visible")
        st.button(label = "Clear chat for current assistant", 
                  on_click=clear_chat_current_agent, 
                  disabled=st.session_state.lock_widgets)
        st.checkbox("🛠️ Show calls to external tools", 
                    key="show_function_calls", 
                    disabled=st.session_state.lock_widgets)

        st.markdown("---")

        # Add user input for API key

        user_key = st.text_input("Set API Key", 
                                 value = st.session_state.user_api_key, 
                                 max_chars=51, type="password", 
                                 help = "Enter your OpenAI API key here to override the default provided by the app.", 
                                 disabled=st.session_state.lock_widgets)
        if user_key != st.session_state.user_api_key and len(user_key) == 51:
            st.session_state.user_api_key = user_key
            update_agents_api_key()
            # write a label like "sk-...lk6" to let the user know a custom key is set and which one
            st.write(f"Using API key: `{user_key[:3]}...{user_key[-3:]}`")


    st.header(st.session_state.current_agent_name)

    current_agent_avatar = st.session_state.agents[st.session_state.current_agent_name].get("avatar", None)
    with st.chat_message("assistant", avatar = current_agent_avatar):
        st.write(st.session_state.agents[st.session_state.current_agent_name]['greeting'])

    for message in st.session_state.agents[st.session_state.current_agent_name]['messages']:
        render_message(message)

    # Check for valid API key and adjust chat input box accordingly
    if has_valid_api_key():
        handle_chat_input()
    else:
        st.chat_input(placeholder="Enter an API key to begin chatting.", disabled=True)



# Main script execution
if __name__ == "__main__":
    initialize_page()
    dotenv.load_dotenv()
    initialize_session_state()
    main()
