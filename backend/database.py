from azure.cosmos import CosmosClient
from main import config  # Importar la configuración segura

def get_cosmos_client():
    return CosmosClient(
        config.get_secret_cached("COSMOS-ENDPOINT"),
        credential=config.get_secret_cached("COSMOS-kEY")
    )

def get_analytics_container():
    client = get_cosmos_client()
    database = client.get_database_client("PromptAnalysis")
    return database.get_container_client("Analytics")

def get_rejected_container():
    client = get_cosmos_client()
    database = client.get_database_client("PromptAnalysis")
    return database.get_container_client("RejectedPrompts")