from tomlkit import item
import weaviate
from weaviate.classes.query import Rerank, Filter, MetadataQuery
from typing import List, Dict, Optional

        
def retrieve(
    query: str,
    collection_name: str,
    metadata: Optional[str] = None,
    top_k: int = 15,
    alpha: float = 0.5,
    use_reranker: bool = False) -> Dict:
    """
    Perform hybrid search (keyword + vector) with optional reranking and filtering.
    
    Args:
        query: The search query string
        collection_name: The name of the collection to search
        metadata: Optional metadata filter as a dictionary
        top_k: Number of results to return
        alpha: Weighting for hybrid search (0 = keyword, 1 = vector)
        use_reranker: Whether to use Weaviate's reranker module
    """
    client = weaviate.connect_to_local(
        port=8080, 
        grpc_port=50051
    )
        
    collection = client.collections.get(collection_name)
    
    # Construct filter
    if metadata:
        filter_list = []
        for key, value in metadata.items():
            filter_list.append(Filter.by_property(key).contains_any([value]))
    
        search_filter = Filter.any_of(filter_list)   
    
    # Perform hybrid search        
    try:
        results = collection.query.hybrid(
            query=query,
            filters=search_filter if metadata else None,
            alpha=alpha,
            limit=top_k,
            rerank=Rerank(
                prop="content",
                query=query
            ) if use_reranker else None,
            return_metadata=MetadataQuery(score=True, distance=True)
        )
        client.close()
        return results
    
    except Exception as e:
        print(f"Error during retrieval: {e}")
        client.close()
        return None

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