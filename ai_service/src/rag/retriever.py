import logging
from weaviate.classes.query import Rerank, Filter, MetadataQuery
from typing import Dict, Optional
from src.core.database import get_weaviate_client

logger = logging.getLogger(__name__)

def retrieve(
    query: str,
    collection_name: str,
    metadata: Optional[Dict] = None,
    top_k: int = 15,
    alpha: float = 0.5,
    use_reranker: bool = False) -> Optional[Dict]:
    """
    Perform hybrid search (keyword + vector) with optional reranking and filtering.
    """
    client = get_weaviate_client()
        
    try:
        collection = client.collections.get(collection_name)
        
        # Construct filter
        search_filter = None
        if metadata:
            filter_list = []
            for key, value in metadata.items():
                filter_list.append(Filter.by_property(key).contains_any([value]))
            
            if filter_list:
                search_filter = Filter.any_of(filter_list)   
        
        # Perform hybrid search        
        results = collection.query.hybrid(
            query=query,
            filters=search_filter,
            alpha=alpha,
            limit=top_k,
            rerank=Rerank(
                prop="content",
                query=query
            ) if use_reranker else None,
            return_metadata=MetadataQuery(score=True, distance=True)
        )
        return results
    
    except Exception as e:
        logger.error(f"Error during retrieval: {e}")
        return None
    # Note: We do NOT close the client here as it is a singleton shared instance


def format_retrieved_documents(results) -> str:
    """Format Weaviate objects into structured string for LLM context."""
    
    if results is None or not results.objects:
        return "No relevant documents found."
    
    formatted_docs = []
    
    for i, obj in enumerate(results.objects, 1):
        doc_parts = [f"[Document {i}]"]
        
        for prop_name, prop_value in obj.properties.items():
            if prop_value is not None:
                if isinstance(prop_value, list):
                    prop_value = ", ".join(str(v) for v in prop_value)
                doc_parts.append(f"{prop_name}: {prop_value}")
        
        formatted_docs.append("\n".join(doc_parts))
    
    return "\n\n".join(formatted_docs)