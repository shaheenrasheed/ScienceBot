import networkx as nx
import pickle
import os
import json
import re
from google import genai
from google.genai import types
from src.config import Config

class SimpleKnowledgeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.graph_path = Config.KG_PATH  # e.g., "data/knowledge_graph.pkl"

    def load_graph(self):
        """Loads existing graph if available to save time/cost."""
        if os.path.exists(self.graph_path):
            print(f"Loading existing Knowledge Graph from {self.graph_path}...")
            with open(self.graph_path, 'rb') as f:
                self.graph = pickle.load(f)
            return True
        return False

    def save_graph(self):
        """Saves the graph to disk."""
        with open(self.graph_path, 'wb') as f:
            pickle.dump(self.graph, f)
        print(f"Knowledge Graph saved to {self.graph_path}")

    def build_graph(self, chunks):
        """
        Builds the graph dynamically using Gemini.
        """
        # 1. Try to load existing graph first
        if self.load_graph():
            print(f"Graph loaded with {self.graph.number_of_nodes()} nodes.")
            return

        print("Building Knowledge Graph dynamically (This takes time)...")
        
        # Limit chunks for testing to save time/tokens (Remove [:5] for full book)
        # We process every chunk to extract real relationships.
        total_chunks = len(chunks)
        
        for i, chunk in enumerate(chunks):
            self._extract_and_add_relations(chunk['text'])
            print(f"Processed chunk {i+1}/{total_chunks} for KG...")

        self.save_graph()
        print(f"Graph built with {self.graph.number_of_nodes()} nodes.")

    def _extract_and_add_relations(self, text):
        """Uses Gemini to extract triples (Subject, Predicate, Object)."""
        
        prompt = f"""
        Analyze the following scientific text and extract knowledge graph triples.
        Return ONLY a JSON list of objects.
        Format: [{{"head": "entity1", "relation": "relationship", "tail": "entity2"}}]
        
        Rules:
        1. Entities should be simple concepts (e.g., "Dobereiner", "Triads", "Atomic Mass").
        2. Relations should be verbs or prepositions (e.g., "proposed", "related_to", "depends_on").
        3. Extract maximum 3 key relationships.
        4. If no relationships found, return [].
        
        TEXT:
        {text[:1000]} 
        """

        try:
            response = self.client.models.generate_content(
                model=Config.LLM_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            # Parse JSON response
            triples = json.loads(response.text)
            
            for item in triples:
                head = item.get('head', '').lower().strip()
                tail = item.get('tail', '').lower().strip()
                relation = item.get('relation', '').lower().strip()
                
                if head and tail and relation:
                    self.graph.add_edge(head, tail, relation=relation)
                    
        except Exception as e:
            # Silently fail on bad chunks to keep the pipeline moving
            pass

    def get_related_concepts(self, query):
        """Finds concepts in query and returns neighbors (1-hop)."""
        query = query.lower()
        related_info = []
        
        # Find partial matches in the graph nodes
        found_nodes = [node for node in self.graph.nodes if node in query or query in node]
        
        # Limit to top 3 matches to avoid noise
        for node in found_nodes[:3]:
            # Get outgoing edges (what does this node do?)
            for neighbor in self.graph.successors(node):
                relation = self.graph[node][neighbor].get('relation', 'related_to')
                related_info.append(f"{node} --[{relation}]--> {neighbor}")
            
            # Get incoming edges (what affects this node?)
            for predecessor in self.graph.predecessors(node):
                relation = self.graph[predecessor][node].get('relation', 'related_to')
                related_info.append(f"{predecessor} --[{relation}]--> {node}")

        return list(set(related_info)) # Remove duplicates