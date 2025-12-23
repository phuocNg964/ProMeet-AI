import weaviate
from src.core.config import settings
import logging

logger = logging.getLogger(__name__)

class WeaviateClient:
    _instance = None
    _client = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = WeaviateClient()
        return cls._instance

    def get_client(self):
        """
        Get or create the Weaviate client.
        In v4, we use connect_to_local or connect_to_custom.
        """
        if self._client is not None and self._client.is_connected():
            return self._client
            
        try:
            # Parse host/port from settings.WEAVIATE_URL if needed, 
            # but for now assuming standard local setup or using explicit ports
            # If settings.WEAVIATE_URL is "http://localhost:8080"
            
            logger.info(f"Connecting to Weaviate at {settings.WEAVIATE_URL}...")
            
            # Using connect_to_local is safest for Docker setups exposed on localhost
            self._client = weaviate.connect_to_local(
                port=8080, # Could extract from Settings if variable
                grpc_port=50051
            )
            
            return self._client
        except Exception as e:
            logger.error(f"Failed to connect to Weaviate: {e}")
            raise e

    def close(self):
        if self._client:
            self._client.close()
            self._client = None
            
# Global helper
def get_weaviate_client():
    return WeaviateClient.get_instance().get_client()
