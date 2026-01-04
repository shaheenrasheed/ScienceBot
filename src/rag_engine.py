from google import genai
from src.config import Config
from src.vector_store import VectorStore
from src.knowledge_graph import SimpleKnowledgeGraph
from src.ingestion import PDFIngestor
from src.logger import GoogleSheetLogger # <--- UPDATED IMPORT
from PIL import Image

class RAGEngine:
    def __init__(self):
        # Initialize Gemini Client
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        
        # Initialize Logger (Google Sheets)
        self.logger = GoogleSheetLogger() # <--- UPDATED INITIALIZATION
        
        # Initialize Data Components
        self.ingestor = PDFIngestor()
        self.vector_store = VectorStore()
        self.kg = SimpleKnowledgeGraph()
        
        # Load Data (Runs only once on startup)
        chunks = self.ingestor.load_and_chunk()
        self.vector_store.create_index(chunks)
        self.kg.build_graph(chunks)

    def route_query(self, query):
        """Decides if the user wants a Quiz or an Explanation."""
        query = query.lower()
        if any(w in query for w in ["quiz", "questions", "test", "exam", "mcq"]): return "Quiz"
        elif any(w in query for w in ["define", "what is", "meaning"]): return "Definition"
        elif any(w in query for w in ["calculate", "solve", "formula"]): return "Numerical"
        elif any(w in query for w in ["summary", "summarize"]): return "Summary"
        else: return "General"

    def get_response(self, query, search_mode="hybrid", chat_history=[], image=None):
        # 1. Route Intent
        q_type = self.route_query(query)
        context_text = ""
        kg_text = ""
        
        # 2. Format Chat History (Context Window)
        history_text = ""
        for msg in chat_history[-5:]:
            role = "Student" if msg["role"] == "user" else "Tutor"
            history_text += f"{role}: {msg['content']}\n"

        print(f"\n🔍 SEARCH MODE: {search_mode.upper()} | INTENT: {q_type} | IMAGE: {image is not None}")

        # 3. Retrieve Context (Fetch MORE for Quizzes)
        k_val = 10 if q_type == "Quiz" else 3 
        
        # Only search if there is a substantial text query
        if len(query.strip()) > 2:
            if search_mode in ["vector", "hybrid"]:
                vector_results = self.vector_store.search(query, k=k_val)
                context_text = "\n".join([c['text'] for c in vector_results])
            
            if search_mode in ["kg", "hybrid"]:
                kg_results = self.kg.get_related_concepts(query)
                kg_text = "\n".join(kg_results)

        # 4. Construct Prompt based on Intent (SPLIT LOGIC)
        
        if q_type == "Quiz":
            # --- QUIZ MODE PROMPT (Strict Q&A List) ---
            prompt_text = f"""
            You are a Strict Exam Setter for 10th Standard Science.
            
            SOURCE TEXT FROM CHAPTER:
            {context_text}
            
            USER REQUEST: {query}
            
            INSTRUCTIONS:
            1. Create clear, numbered questions based ONLY on the source text.
            2. **Format strictly like this:**
               
               **Q1:** [Question text here?]
               *Answer:* [Answer text here]
               
               ---
               **Q2:** [Next question?]
               *Answer:* [Next answer]
               
            3. Do NOT group them into a paragraph.
            4. Do not use filler intro text. Start immediately with Q1.
            """
            
        else:
            # --- TUTOR MODE PROMPT (Structured Study Guide) ---
            prompt_text = f"""
            You are an expert 10th Standard Science Tutor.
            
            CONVERSATION HISTORY:
            {history_text}
            
            CURRENT QUESTION: {query}
            
            TEXTBOOK CONTEXT:
            {context_text if context_text else "No textbook context found."}
            
            KNOWLEDGE GRAPH INSIGHTS:
            {kg_text}
            
            INSTRUCTIONS:
            1. **Direct Answer:** Start with a 1-sentence direct summary.
            2. **Structure:** Use `### Headings` for main ideas.
            3. **Bullets:** Use bullet points for steps, lists, or properties.
            4. **Spacing:** Leave an empty line between every section.
            5. **Key Terms:** **Bold** important scientific terms.
            6. **Visuals:** If describing a diagram (like a cell or circuit), break it down step-by-step.
            7. **Tone:** Encouraging and clear.
            """

        # 5. Generate Answer
        try:
            content_payload = [prompt_text]
            if image:
                content_payload.append(image)

            response = self.client.models.generate_content(
                model=Config.LLM_MODEL,
                contents=content_payload
            )
            answer = response.text
        except Exception as e:
            answer = f"Error: {e}"
        
        # 6. Log to Google Sheets
        self.logger.log_interaction(query, answer, q_type)
        
        return answer