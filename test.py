from src.utils.db import mongo

try:
    config = mongo.get_app_config()
    port = config["routes"][0]
    print(port)
finally:
    mongo.close()