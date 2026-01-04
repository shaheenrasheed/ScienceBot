import sys
from src.rag_engine import RAGEngine

def main():
    print("========================================")
    print(" 🔬 10th Science Bot (Hybrid Mode) ")
    print("========================================")
    print("Initializing...")
    
    engine = RAGEngine()
    
    print("\n✅ READY! Commands:")
    print(" - Type your question normally for HYBRID search.")
    print(" - Type '/v your query' for VECTOR ONLY.")
    print(" - Type '/k your query' for KG ONLY.")
    print(" - Type 'exit' to quit.\n")
    
    while True:
        user_input = input("Student: ").strip()
        
        if user_input.lower() in ['exit', 'quit']:
            break
        
        # Default mode
        mode = "hybrid"
        query = user_input
        
        # Check for commands
        if user_input.startswith("/v "):
            mode = "vector"
            query = user_input[3:]
        elif user_input.startswith("/k "):
            mode = "kg"
            query = user_input[3:]
            
        print("\nBot is thinking...")
        try:
            answer = engine.get_response(query, search_mode=mode)
            print(f"\nScienceBot: {answer}\n")
            print("-" * 50)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()