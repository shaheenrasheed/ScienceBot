cat <<EOF > README.md
# 🔬 10th Standard Science AI Tutor

An advanced RAG (Retrieval-Augmented Generation) Chatbot built with Python, Google Gemini, and Streamlit.

## Features
- **Hybrid Search:** Combines Vector Search (FAISS) and Knowledge Graph (NetworkX).
- **Multimodal:** Understands text and analyzes uploaded science diagrams.
- **Dual Modes:** Explains concepts like a Tutor or generates Quizzes like an Examiner.
- **Cloud Logging:** Logs all student interactions to Google Sheets.
- **Interactive Graph:** Visualizes science concepts using PyVis.

## Setup
1. Clone the repo.
2. Install dependencies: \`pip install -r requirements.txt\`.
3. Add your \`gemini_api_key\` to a \`.env\` file.
4. Run: \`streamlit run web_app.py\`.



## 📽️ Project Presentation
Click the image below to view the full slide deck explaining the Architecture and Logic:

[![ScienceBot Presentation](assets/teacher.png)](https://gamma.app/docs/ScienceBot-iwd6gwqgbhns71k)
