"""
Wynn Concierge Vector Store
RAG-based knowledge retrieval with guest-aware filtering
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import time

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
VECTOR_STORE_DIR = DATA_DIR / "faiss_index"


class ResortKnowledgeBase:
    """
    Vector store for resort amenities with guest-aware filtering.
    Implements RAG (Retrieval Augmented Generation) for personalized recommendations.
    """
    
    def __init__(self, openai_api_key: str, force_rebuild: bool = False):
        """
        Initialize the knowledge base.
        
        Args:
            openai_api_key: OpenAI API key for embeddings
            force_rebuild: Force rebuild of vector store even if cached version exists
        """
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=openai_api_key,
            model="text-embedding-3-small",
            max_retries=5,  # Increased retries for rate limits
            request_timeout=60  # Longer timeout for retries
        )
        self.resort_data = self._load_resort_data()
        self.vector_store = self._build_or_load_vector_store(force_rebuild)
        logger.info(f"✅ Knowledge base initialized with {len(self.resort_data)} venues")
    
    def _load_resort_data(self) -> List[Dict]:
        """Load resort data from JSON with validation"""
        resort_file = DATA_DIR / "resort_data.json"
        
        if not resort_file.exists():
            raise FileNotFoundError(
                f"Resort data not found at {resort_file}. "
                "Run data_generator.py first."
            )
        
        try:
            with open(resort_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if not isinstance(data, list) or len(data) == 0:
                raise ValueError(f"Invalid resort data format in {resort_file}")
                
            logger.info(f"📊 Loaded {len(data)} venues from resort data")
            return data
            
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Failed to parse resort data JSON: {e}. "
                "The file may be corrupted. Try regenerating with data_generator.py"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load resort data: {e}")
    
    def _create_documents(self) -> List[Document]:
        """Convert resort data into LangChain Documents with rich metadata"""
        documents = []
        
        for venue in self.resort_data:
            # Create a rich text representation for embedding
            content = f"""
            Venue: {venue['name']}
            Category: {venue['category']}
            Description: {venue['description']}
            Ambiance: {', '.join(venue['tags'])}
            Dietary Options: {', '.join(venue['dietary_options'])}
            Hours: {venue['opening_hours']}
            Price Level: {venue['price_tier']}
            VIP Benefits: {venue['vip_perks']}
            """
            
            # Store full venue data in metadata
            metadata = {
                'id': venue['id'],
                'name': venue['name'],
                'category': venue['category'],
                'tags': venue['tags'],
                'dietary_options': venue['dietary_options'],
                'allergen_warnings': venue['allergen_warnings'],
                'constraints': venue['constraints'],
                'opening_hours': venue['opening_hours'],
                'average_duration_minutes': venue['average_duration_minutes'],
                'price_tier': venue['price_tier'],
                'vip_perks': venue['vip_perks']
            }
            
            documents.append(Document(page_content=content, metadata=metadata))
        
        return documents
    
    def _build_or_load_vector_store(self, force_rebuild: bool) -> FAISS:
        """Build vector store or load from cache using FAISS native methods"""
        
        # Check if cached version exists (FAISS native format)
        if VECTOR_STORE_DIR.exists() and not force_rebuild:
            try:
                logger.info("📦 Loading cached vector store...")
                # Check if index file exists before attempting to load
                index_file = VECTOR_STORE_DIR / "index.faiss"
                if not index_file.exists():
                    logger.warning("⚠️  FAISS index file not found, rebuilding...")
                else:
                    # Load using FAISS native method (no pickle, no threading issues)
                    vector_store = FAISS.load_local(
                        str(VECTOR_STORE_DIR),
                        self.embeddings,
                        allow_dangerous_deserialization=True  # Safe for our controlled data
                    )
                    logger.info("✅ Vector store loaded from cache")
                    return vector_store
            except EOFError as e:
                logger.warning(f"⚠️  Corrupted cache file (EOFError): {e}")
                logger.info("🔨 Rebuilding vector store...")
            except Exception as e:
                logger.warning(f"⚠️  Failed to load cached vector store: {e}")
                logger.info("🔨 Rebuilding vector store...")
        
        logger.info("🔨 Building new vector store...")
        
        # Create documents
        documents = self._create_documents()
        
        # Split documents (though our venue docs are already appropriately sized)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        split_docs = text_splitter.split_documents(documents)
        
        # Create FAISS vector store with retry logic for rate limits
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                vector_store = FAISS.from_documents(split_docs, self.embeddings)
                break
            except Exception as e:
                if '429' in str(e) and attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"⚠️  Rate limit hit, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise
        
        # Cache the vector store using FAISS native save (not pickle)
        VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
        vector_store.save_local(str(VECTOR_STORE_DIR))
        
        logger.info(f"💾 Vector store cached to {VECTOR_STORE_DIR}")
        
        return vector_store
    
    def _check_dietary_safety(self, venue: Dict, dietary_restrictions: str) -> Tuple[bool, Optional[str]]:
        """
        Check if venue is safe for guest's dietary restrictions.
        
        Returns:
            (is_safe, reason) tuple
        """
        if not dietary_restrictions or dietary_restrictions.lower() == 'none':
            return True, None
        
        restrictions = [r.strip().lower() for r in dietary_restrictions.split(',')]
        allergen_warnings = [a.lower() for a in venue.get('allergen_warnings', [])]
        dietary_options = [o.lower() for o in venue.get('dietary_options', [])]
        
        # Critical safety checks (allergens)
        if 'nut allergy' in restrictions or 'nut' in restrictions:
            if any('nut' in warning or 'peanut' in warning for warning in allergen_warnings):
                return False, "Contains nuts - ALLERGY RISK"
        
        if 'shellfish allergy' in restrictions or 'shellfish' in restrictions:
            if any('shellfish' in warning for warning in allergen_warnings):
                return False, "Contains shellfish - ALLERGY RISK"
        
        # Dietary preference checks (softer constraints)
        if 'vegetarian' in restrictions:
            if 'vegetarian' not in dietary_options and venue['category'] == 'Fine Dining':
                if 'steakhouse' in venue['name'].lower() or 'seafood' in ' '.join(venue['tags']).lower():
                    return False, "Limited vegetarian options available"
        
        if 'vegan' in restrictions:
            if 'vegan' not in dietary_options:
                return False, "No dedicated vegan options"
        
        if 'gluten-free' in restrictions or 'gluten free' in restrictions:
            if not any('gluten' in option for option in dietary_options):
                if 'pizza' in venue['name'].lower() or 'pasta' in venue['description'].lower():
                    return False, "Limited gluten-free options"
        
        if 'halal' in restrictions:
            if 'halal' not in dietary_options and any('pork' in warning.lower() for warning in allergen_warnings):
                return False, "Not certified Halal"
        
        return True, None
    
    def _check_time_availability(self, venue: Dict, requested_time: Optional[str] = None) -> bool:
        """Check if venue is open at requested time (simplified)"""
        # This is a basic check - in production this would query real-time availability
        return True  # For now, assume all venues are available
    
    def search_amenities(
        self,
        query: str,
        guest_profile: Optional[Dict] = None,
        k: int = 5,
        filter_category: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for venues matching query with guest-aware filtering.
        
        Args:
            query: Natural language search query
            guest_profile: Guest profile with dietary restrictions
            k: Number of results to return
            filter_category: Optional category filter (e.g., "Fine Dining")
        
        Returns:
            List of venue dictionaries with safety notes
        """
        # Input validation
        if not query or not query.strip():
            logger.warning("Empty search query provided")
            return []
        
        if k <= 0:
            logger.warning(f"Invalid k value: {k}, using default k=5")
            k = 5
        
        # Perform semantic search
        results = self.vector_store.similarity_search(query, k=k*2)  # Get more for filtering
        
        # Convert to venue dictionaries
        venues = []
        for doc in results:
            venue_id = doc.metadata['id']
            venue_data = next((v for v in self.resort_data if v['id'] == venue_id), None)
            
            if venue_data:
                # Apply category filter if specified
                if filter_category and venue_data['category'] != filter_category:
                    continue
                
                # Check dietary safety
                is_safe = True
                safety_note = None
                
                if guest_profile and 'dietary_restrictions' in guest_profile:
                    is_safe, safety_note = self._check_dietary_safety(
                        venue_data,
                        guest_profile['dietary_restrictions']
                    )
                
                venue_result = {
                    **venue_data,
                    'is_safe': is_safe,
                    'safety_note': safety_note,
                    'relevance_score': doc.metadata.get('score', 1.0)
                }
                
                venues.append(venue_result)
        
        # Prioritize safe options, then by relevance
        venues.sort(key=lambda x: (not x['is_safe'], -x['relevance_score']))
        
        return venues[:k]
    
    def get_venue_by_id(self, venue_id: str) -> Optional[Dict]:
        """Get venue by ID"""
        return next((v for v in self.resort_data if v['id'] == venue_id), None)
    
    def get_venues_by_category(self, category: str) -> List[Dict]:
        """Get all venues in a category"""
        return [v for v in self.resort_data if v['category'] == category]
    
    def get_all_categories(self) -> List[str]:
        """Get all unique categories"""
        return list(set(v['category'] for v in self.resort_data))


def demo():
    """Demo function to test the knowledge base"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return
    
    # Initialize knowledge base
    kb = ResortKnowledgeBase(api_key, force_rebuild=True)
    
    # Test guest profile
    guest = {
        'name': 'Sarah Chen',
        'dietary_restrictions': 'Vegetarian, Gluten-Free'
    }
    
    # Test search
    print("\n🔍 Testing: 'romantic dinner with wine'")
    results = kb.search_amenities(
        "romantic dinner with wine",
        guest_profile=guest,
        k=3
    )
    
    for i, venue in enumerate(results, 1):
        print(f"\n{i}. {venue['name']} ({venue['category']})")
        print(f"   Safe: {'✅' if venue['is_safe'] else '❌'}")
        if venue['safety_note']:
            print(f"   Note: {venue['safety_note']}")
    
    print("\n✅ Demo complete!")


if __name__ == "__main__":
    demo()
