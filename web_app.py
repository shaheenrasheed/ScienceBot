import streamlit as st
import time
from pyvis.network import Network
import streamlit.components.v1 as components
from src.rag_engine import RAGEngine
import tempfile
from PIL import Image
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="10th Science AI Tutor",
    page_icon="🔬",
    layout="wide"
)

# --- AVATAR SETUP ---
# Path to your teacher image
TEACHER_IMAGE = "assets/teacher.png"

# Fallback if image is missing
if not os.path.exists(TEACHER_IMAGE):
    st.warning(f"Teacher image not found at {TEACHER_IMAGE}. Using default emoji.")
    TEACHER_AVATAR = "👨‍🏫"
else:
    TEACHER_AVATAR = TEACHER_IMAGE

STUDENT_AVATAR = "🧑‍🎓"

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    # Display Teacher Image in Sidebar
    if os.path.exists(TEACHER_IMAGE):
        st.image(TEACHER_IMAGE, width=120)
    else:
        st.image("https://cdn-icons-png.flaticon.com/512/2021/2021646.png", width=100)
        
    st.title("Settings")
    
    # 1. Search Mode Toggle
    mode = st.radio(
        "Search Mode",
        ["Hybrid (Best)", "Vector Only", "Knowledge Graph Only"],
        index=0
    )
    
    mode_map = {"Hybrid (Best)": "hybrid", "Vector Only": "vector", "Knowledge Graph Only": "kg"}
    selected_mode = mode_map[mode]
    
    st.divider()
    
    # 2. Image Upload
    st.markdown("### 📸 Upload Image")
    uploaded_file = st.file_uploader("Upload a diagram or question", type=["jpg", "png", "jpeg"])
    
    image_input = None
    if uploaded_file:
        image_input = Image.open(uploaded_file)
        st.image(image_input, caption="Uploaded Image", use_container_width=True)
        st.caption("Image will be sent with your next question.")

    st.divider()
    
    # 3. Stats
    st.markdown("### 📊 System Status")
    if "engine" in st.session_state:
        node_count = st.session_state.engine.kg.graph.number_of_nodes()
        st.metric("KG Nodes", node_count)
    
    st.caption("Running on: MacBook M3")

# --- INITIALIZE ENGINE ---
@st.cache_resource
def load_engine():
    return RAGEngine()

if "engine" not in st.session_state:
    with st.spinner("🧠 Loading Textbook & Building Graph..."):
        st.session_state.engine = load_engine()
        st.success("System Ready!")

# --- VISUALIZATION FUNCTION ---
def visualize_graph(engine):
    net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white", directed=True)
    if engine.kg.graph.number_of_nodes() > 100:
        degrees = dict(engine.kg.graph.degree())
        top_nodes = sorted(degrees, key=degrees.get, reverse=True)[:100]
        G_sub = engine.kg.graph.subgraph(top_nodes)
        net.from_nx(G_sub)
    else:
        net.from_nx(engine.kg.graph)
    
    net.repulsion(node_distance=120, central_gravity=0.33, spring_length=110, spring_strength=0.10, damping=0.95)
    try:
        path = tempfile.gettempdir() + "/knowledge_graph.html"
        net.save_graph(path)
        with open(path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        return source_code
    except Exception as e:
        return None

# --- MAIN INTERFACE ---
st.title("🔬 10th Standard Science Chatbot")

tab1, tab2 = st.tabs(["💬 Chat", "🕸️ Knowledge Graph"])

# === TAB 1: CHAT ===
with tab1:
    # 1. Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 2. Display Chat History with Avatars
    for message in st.session_state.messages:
        avatar = TEACHER_AVATAR if message["role"] == "assistant" else STUDENT_AVATAR
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # 3. Handle User Input (Fixed at Bottom)
    if prompt := st.chat_input("Ask a question or explain the uploaded image..."):
        
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=STUDENT_AVATAR):
            st.markdown(prompt)

        # Generate Response
        with st.chat_message("assistant", avatar=TEACHER_AVATAR):
            message_placeholder = st.empty()
            full_response = ""
            
            with st.spinner("Thinking..."):
                # Call engine with Image (if uploaded)
                response = st.session_state.engine.get_response(
                    prompt, 
                    search_mode=selected_mode,
                    chat_history=st.session_state.messages,
                    image=image_input
                )
                
                # Streaming Output
                for chunk in response.split():
                    full_response += chunk + " "
                    time.sleep(0.02) 
                    message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
        
        # Add assistant message
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# === TAB 2: VISUALIZATION ===
with tab2:
    st.header("Interactive Knowledge Graph")
    if st.button("Generate Graph Visualization"):
        with st.spinner("Rendering Physics..."):
            html_data = visualize_graph(st.session_state.engine)
            if html_data:
                components.html(html_data, height=650, scrolling=True)