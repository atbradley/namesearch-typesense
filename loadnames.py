import configparser
import csv
import logging
from itertools import chain

from metaphone import doublemetaphone

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

logging.info("Creating Schema.")
# TODO: Need to store dates so we can search on them.
doc_schema = {
    "name": TYPESENSE_COLLECTION,
    "fields": [
        {"name": "name", "type": "string"},
        {"name": "address_1", "type": "string"},
        {"name": "address_2", "type": "string"},
        {"name": "metaphones", "type": "string[]"},
        {
            "name": "embedding",
            "type": "float[]",
            "embed": {
                "from": [
                    "name",
                    "address_1", "address_2"
                ],
                "model_config": {"model_name": "ts/e5-large-v2"},
            },
        },
    ],
    "enable_nested_fields": False,
}

# Initialize the Typesense client
client = typesense.Client(
    {
        "api_key": TYPESENSE_API_KEY,
        "nodes": [
            {
                "host": TYPESENSE_HOST,
                "port": TYPESENSE_PORT,
                "protocol": TYPESENSE_PROTOCOL,
            }
        ],
        "connection_timeout_seconds": 30,
    }
)

# Create the collection
try:
    client.collections[TYPESENSE_COLLECTION].delete()
except Exception as e:
    logging.error(e)

client.collections.create(doc_schema)

logging.info("Collection '%s' created." % TYPESENSE_COLLECTION)
logging.info("Reading data from file.")
# Load the data from fake_names.csv using the csv module
with open("fake_names.csv") as f:
    reader = csv.DictReader(f)
    documents = list(reader)

docs = [
    doc | {"metaphones": list(chain.from_iterable([doublemetaphone(x) for x in doc['name'].split()]))}
    for doc in documents
]

print(docs[:5])

logging.info("Loading data into collection '%s'..." % TYPESENSE_COLLECTION)

resp = client.collections[TYPESENSE_COLLECTION].documents.import_(
    docs, {"action": "create"}
)

for err in [r for r in resp if not r["success"]]:
    logging.error(f"Error {err['error']}; Document {err['document']} ")

logging.info("Done!")
