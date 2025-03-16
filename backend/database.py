import os
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def get_cosmos_container():
    try:
        client = CosmosClient(os.getenv("COSMOS_ENDPOINT"), credential=os.getenv("COSMOS_KEY"))
        database = client.get_database_client("PromptAnalysis")
        return database.get_container_client("Analytics")
    except CosmosHttpResponseError as e:
        raise RuntimeError(f"Error de conexión a Cosmos DB: {str(e)}")