from dotenv import load_dotenv
import streamlit as st
from langchain_groq import ChatGroq
import sqlite3
import os
import time


# CONFIG


load_dotenv()

st.set_page_config(
    page_title="Nova AI",
    page_icon="🚀",
    layout="wide"
)

# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>

/* Animated Gradient Title */
.title {
    font-size: 3rem;
    font-weight: bold;
    text-align: center;
    background: linear-gradient(
        90deg,
        #00c6ff,
        #0072ff,
        #8e2de2,
        #ff0080
    );
    background-size: 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: gradient 6s ease infinite;
}

@keyframes gradient {
    0% {background-position: 0%;}
    50% {background-position: 100%;}
    100% {background-position: 0%;}
}

.stChatMessage {
    animation: fadeIn 0.4s ease-in-out;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0px);
    }
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# DATABASE
# ==========================================

def init_db():
    conn = sqlite3.connect("nova_chat.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS chat_history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

def save_message(role, content):
    conn = sqlite3.connect("nova_chat.db")
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO chat_history(role, content) VALUES (?, ?)",
        (role, content)
    )

    conn.commit()
    conn.close()

def load_messages():
    conn = sqlite3.connect("nova_chat.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT role, content
        FROM chat_history
        ORDER BY id ASC
    """)

    rows = cur.fetchall()

    conn.close()

    return [
        {"role": row[0], "content": row[1]}
        for row in rows
    ]

def clear_history():
    conn = sqlite3.connect("nova_chat.db")
    cur = conn.cursor()

    cur.execute("DELETE FROM chat_history")

    conn.commit()
    conn.close()

# Initialize DB
init_db()

# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.title("🚀 Nova AI")

    st.markdown("Powered by Groq")

    temperature = st.slider(
        "Creativity",
        0.0,
        1.0,
        0.3,
        0.1
    )

    st.divider()

    if st.button(
        "🗑 Delete Chat History",
        use_container_width=True
    ):
        clear_history()

        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! I'm Nova AI. How can I help you?"
            }
        ]

        st.success("History Deleted")
        st.rerun()

# ==========================================
# API KEY CHECK
# ==========================================

if not os.getenv("GROQ_API_KEY"):
    st.error("GROQ_API_KEY not found in .env")
    st.stop()

# ==========================================
# LLM
# ==========================================

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=temperature
)

# ==========================================
# SESSION STATE
# ==========================================

if "messages" not in st.session_state:

    history = load_messages()

    if history:
        st.session_state.messages = history
    else:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! I'm Nova AI. How can I help you?"
            }
        ]

# ==========================================
# TITLE
# ==========================================

st.markdown(
    '<div class="title">🚀 NOVA AI</div>',
    unsafe_allow_html=True
)

st.caption("Your Intelligent AI Assistant")

# ==========================================
# DISPLAY CHAT
# ==========================================

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==========================================
# USER INPUT
# ==========================================

prompt = st.chat_input(
    "Ask Nova anything..."
)

if prompt:

    # USER MESSAGE
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    save_message("user", prompt)

    with st.chat_message("user"):
        st.markdown(prompt)

    try:

        # AI RESPONSE
        response = llm.invoke(
            [
                {
                    "role": "system",
                    "content": """
                    You are Nova AI,
                    a smart, helpful,
                    professional AI assistant.
                    """
                },
                *st.session_state.messages
            ]
        )

        assistant_response = response.content

        # Typing Animation
        with st.chat_message("assistant"):

            placeholder = st.empty()

            displayed_text = ""

            for char in assistant_response:

                displayed_text += char

                placeholder.markdown(
                    displayed_text + "▌"
                )

                time.sleep(0.01)

            placeholder.markdown(
                displayed_text
            )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": assistant_response
            }
        )

        save_message(
            "assistant",
            assistant_response
        )

    except Exception as e:
        st.error(
            f"Error: {str(e)}"
        )