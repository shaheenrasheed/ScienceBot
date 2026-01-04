import fitz  # PyMuPDF
from src.config import Config

class PDFIngestor:
    def __init__(self):
        self.pdf_path = Config.PDF_PATH

    def load_and_chunk(self):
        """Extracts text and splits into chunks."""
        doc = fitz.open(self.pdf_path)
        chunks = []
        
        print("Creating chunks...")
        for page_num, page in enumerate(doc):
            text = page.get_text()
            # Simple chunking by paragraphs (double newline)
            paragraphs = text.split('\n\n')
            
            for para in paragraphs:
                clean_text = para.strip()
                if len(clean_text) > 50: # Ignore tiny headers/footers
                    chunks.append({
                        "text": clean_text,
                        "metadata": {
                            "page": page_num + 1,
                            "source": "textbook"
                        }
                    })
        
        print(f"Total chunks created: {len(chunks)}")
        return chunks