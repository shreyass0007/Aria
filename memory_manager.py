import os
import chromadb
from chromadb.config import Settings
from datetime import datetime
from dotenv import load_dotenv
import openai

load_dotenv()

class MemoryManager:
    """
    Manages long-term memory using ChromaDB for semantic search across all conversations.
    Embeds and stores conversation messages for retrieval based on semantic similarity.
    """
    
    def __init__(self):
        """Initialize ChromaDB and OpenAI for embeddings."""
        self.openai_api_key = os.getenv("OPEN_AI_API_KEY")
        
        # Initialize OpenAI client
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        else:
            print("[WARNING] OPEN_AI_API_KEY not found. Long-term memory disabled.")
            self.client = None
            self.collection = None
            return
        
        # Configuration
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        self.similarity_threshold = float(os.getenv("SIMILARITY_THRESHOLD", "0.4"))
        self.max_results = int(os.getenv("MAX_LONG_TERM_RESULTS", "5"))
        
        # Initialize ChromaDB
        db_path = os.getenv("CHROMADB_PATH", "./vector_db")
        try:
            self.client = chromadb.PersistentClient(path=db_path)
            
            # Get or create collection with Cosine similarity
            self.collection = self.client.get_or_create_collection(
                name="aria_conversations_v2",
                metadata={"hnsw:space": "cosine", "description": "Long-term conversation memory for Aria"}
            )
            
            print(f"[OK] ChromaDB initialized at {db_path}")
            print(f"[INFO] Collection contains {self.collection.count()} messages")
        except Exception as e:
            print(f"[ERROR] Failed to initialize ChromaDB: {e}")
            self.client = None
            self.collection = None
    
    def is_available(self) -> bool:
        """Check if memory manager is available."""
        return self.client is not None and self.collection is not None
    
    def _get_embedding(self, text: str) -> list:
        """Generate embedding for text using OpenAI."""
        try:
            response = openai.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"[ERROR] Failed to generate embedding: {e}")
            return None
    
    def add_message(self, conversation_id: str, message: str, role: str, timestamp: str = None):
        """
        Add a message to the vector database.
        
        Args:
            conversation_id: UUID of the conversation
            message: The message content
            role: 'user' or 'assistant'
            timestamp: ISO timestamp (optional, defaults to now)
        """
        if not self.is_available():
            return False
        
        try:
            # Generate embedding
            embedding = self._get_embedding(message)
            if not embedding:
                return False
            
            # Create unique ID for this message
            message_id = f"{conversation_id}_{timestamp or datetime.utcnow().isoformat()}"
            
            # Prepare metadata
            metadata = {
                "conversation_id": conversation_id,
                "role": role,
                "timestamp": timestamp or datetime.utcnow().isoformat()
            }
            
            # Add to collection
            self.collection.add(
                ids=[message_id],
                embeddings=[embedding],
                documents=[message],
                metadatas=[metadata]
            )
            
            return True
        except Exception as e:
            print(f"[ERROR] Failed to add message to memory: {e}")
            return False
    
    def search_relevant_context(self, query: str, top_k: int = None, exclude_conversation: str = None) -> list:
        """
        Search for semantically similar messages across all conversations.
        
        Args:
            query: The search query
            top_k: Number of results to return (defaults to self.max_results)
            exclude_conversation: Optional conversation ID to exclude from results
        
        Returns:
            List of dicts: [{"text": str, "conversation_id": str, "role": str, "timestamp": str, "similarity": float}]
        """
        if not self.is_available():
            return []
        
        try:
            # Generate query embedding
            query_embedding = self._get_embedding(query)
            if not query_embedding:
                return []
            
            # Search in collection
            k = top_k or self.max_results
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k * 2  # Get extra results for filtering
            )
            
            # Process results
            relevant_messages = []
            
            if results and results['documents'] and len(results['documents']) > 0:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i]
                    distance = results['distances'][0][i]
                    
                    # Convert distance to similarity (cosine similarity = 1 - distance)
                    similarity = 1 - distance
                    
                    # Filter by threshold and exclude current conversation
                    if similarity >= self.similarity_threshold:
                        if exclude_conversation and metadata.get('conversation_id') == exclude_conversation:
                            continue
                        
                        relevant_messages.append({
                            "text": doc,
                            "conversation_id": metadata.get("conversation_id"),
                            "role": metadata.get("role"),
                            "timestamp": metadata.get("timestamp"),
                            "similarity": round(similarity, 3)
                        })
                    
                    # Stop if we have enough results
                    if len(relevant_messages) >= k:
                        break
            
            return relevant_messages
        except Exception as e:
            print(f"[ERROR] Failed to search memory: {e}")
            return []
    
    def get_stats(self) -> dict:
        """Get statistics about the memory database."""
        if not self.is_available():
            return {"available": False}
        
        try:
            count = self.collection.count()
            return {
                "available": True,
                "total_messages": count,
                "embedding_model": self.embedding_model,
                "similarity_threshold": self.similarity_threshold
            }
        except Exception as e:
            print(f"[ERROR] Failed to get stats: {e}")
            return {"available": False, "error": str(e)}
    
    def clear_memory(self):
        """Clear all stored memories. USE WITH CAUTION!"""
        if not self.is_available():
            return False
        
        try:
            # Delete and recreate collection
            try:
                self.client.delete_collection("aria_conversations_v2")
            except ValueError:
                pass # Collection might not exist
                
            self.collection = self.client.create_collection(
                name="aria_conversations_v2",
                metadata={"hnsw:space": "cosine", "description": "Long-term conversation memory for Aria"}
            )
            print("[OK] Memory cleared")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to clear memory: {e}")
            return False
