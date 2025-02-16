import configparser
import logging
import os

import typesense

config = configparser.ConfigParser()
config.read("config.ini")

LOG_LEVEL = config.get("logging", "level", fallback="INFO")
LOG_FILE = config.get("logging", "file", fallback="namesearch.log")

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)

TYPESENSE_API_KEY = config.get("typesense", "api_key")
TYPESENSE_HOST = config.get("typesense", "host", fallback="localhost")
TYPESENSE_PORT = config.get("typesense", "port", fallback="8108")
TYPESENSE_PROTOCOL = config.get("typesense", "protocol", fallback="http")
TYPESENSE_COLLECTION = config.get("typsense", "collection", fallback="namesearch")

logging.info("Connecting to Typesense...")
client = typesense.Client(
    {
        "nodes": [
            {
                "host": TYPESENSE_HOST,
                "port": TYPESENSE_PORT,
                "protocol": TYPESENSE_PROTOCOL,
            }
        ],
        "api_key": TYPESENSE_API_KEY,
        "connection_timeout_seconds": 2,
    }
)

logging.info("Beginning query loop. Querying collection %s" % TYPESENSE_COLLECTION)

docs_coll = client.collections[TYPESENSE_COLLECTION].retrieve()
logging.info(
    f"Collection '{TYPESENSE_COLLECTION}' has {docs_coll['num_documents']} documents"
)

while True:
    query = input("Enter a query or 'q' to quit: ")
    if query == "q":
        break

    search_parameters = {
        "collection": TYPESENSE_COLLECTION,
        "q": query,
        "query_by": "embedding, name",
        "vector_query": "embedding:([], alpha: 0.8)",
        #"query_by_weights": "10,3",
        #"query_by": "embedding",
        "exclude_fields": "embedding",
        "prefix": False,
        "remote_embedding_timeout_ms": 5000,
        "remote_embedding_num_try": 3,
        "per_page": 5,
    }

    try:
        response = client.collections[TYPESENSE_COLLECTION].documents.search(
            search_parameters
        )
    except Exception:
        logging.info("No results found")
        continue
    for hit in response["hits"]:
        doc = hit["document"]
        print(doc.get("name"), doc.get("address_1", ""), doc.get("address_2", ""))
        print(hit.get("vector_distance", ""))
        print("-------------------------------")
    print("\n")
