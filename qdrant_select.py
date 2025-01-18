from utils.qdrant_control import qdrant_manager
from dotenv import dotenv_values


config = dotenv_values("./.env")
qdrant_obj = qdrant_manager(None, config.get("qdrant_url"), config.get("qdrant_api_key"))

print("Qdrant 內目前總資料 : \n", "="*50)
qdrant_obj.get_collections()


qdrant_manager('view_restaurant_test', config.get("qdrant_url"), config.get("qdrant_api_key")).create_collection()
