import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/ask"

st.set_page_config(
    page_title="AI Tech Consultant",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 AI Tech Consultant")
st.caption("Your AI assistant, powered by your product knowledge base.")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! 👋 Ask me a question about "
                "the product documentation."
            ),
            "sources": []
        }
    ]

with st.sidebar:
    st.header("About")
    st.write("Answers are generated using your knowledge base and Groq AI.")
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        for source in message.get("sources", []):
            if source.get("url"):
                st.markdown(
                    f"- [{source.get('title', 'Source article')}]"
                    f"({source['url']})"
                )

prompt = st.chat_input("Ask your technical question...")

if prompt:
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "sources": []
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Searching your knowledge base..."):
                response = requests.post(
                    API_URL,
                    json={"query": prompt},
                    timeout=120
                )
                response.raise_for_status()
                result = response.json()

            answer = result.get(
                "answer",
                "Sorry, I couldn't generate an answer."
            )
            sources = result.get("sources", [])

            st.markdown(answer)

            if sources:
                st.markdown("*Sources*")
                for source in sources:
                    if source.get("url"):
                        st.markdown(
                            f"- [{source.get('title', 'Source article')}]"
                            f"({source['url']})"
                        )

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources
            })

        except requests.RequestException as error:
            st.error(
                "Could not reach the AI API. "
                "Check that FastAPI is running on port 8000."
            )
            st.caption(str(error))