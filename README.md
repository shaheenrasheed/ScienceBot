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
2. Make sure you have Python installed. Then run: pip install -r requirements.txt
3. Create a .env file: Inside the data/ folder, create a new file named .env and Add your Google Gemini API Key inside it: GEMINI_API_KEY=AIzaSyDxxxxxxxxx_YOUR_KEY_HERE
4. If you want the bot to save chat logs, follow these steps. If not, skip this!
    1. Get the Key:
        * Go to Google Cloud Console.
        * Create a new project.
        * Search for "Google Sheets API" and "Google Drive API" and Enable both.
        * Go to Credentials → Create Credentials → Service Account.
        * Click the Keys tab → Add Key → Create new key (JSON).
        * A file will download. Rename it to credentials.json and put it in the data/ folder.
    2. Share the Sheet:
        * Open your credentials.json file and copy the client_email address (it looks like robot@project.iam.gserviceaccount.com).
        * Create a new Google Sheet named "ScienceBot Logs".
        * Click Share (top right) and paste that email address. Give it Editor access.


    If you don't have one, the bot will simply skip logging (it will still work!).
5. Run: \`streamlit run web_app.py\`.



## 📽️ Project Presentation
Click the image below to view the full slide deck explaining the Architecture and Logic:

[![ScienceBot Presentation](assets/teacher.png)](https://gamma.app/docs/ScienceBot-iwd6gwqgbhns71k)
