
import json
import tempfile
import time
from pathlib import Path

from backend.config import get_client, BASE_DIR

# Store information locally
CONFIG_FILE = BASE_DIR / "data" / "config.json"


def get_saved_store():

    if CONFIG_FILE.exists():

        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)

        return config.get("file_search_store")


    return None


def create_file_search_store():

    client = get_client()

    store = client.file_search_stores.create(
        config={
            "display_name": "Personal AI Knowledge Base",
            "embedding_model": "models/gemini-embedding-2"
        }
    )

    # Save store ID locally
    config = {
        "file_search_store": store.name
    }

    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)

    return store.name


def get_or_create_store():

    store_name = get_saved_store()

    if store_name:
        return store_name

    return create_file_search_store()


def upload_document(uploaded_file):

    client = get_client()

    # Get the persistent knowledge base
    store_name = get_or_create_store()

    # Temporarily save uploaded file
    suffix = Path(uploaded_file.name).suffix

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as temp_file:

        temp_file.write(uploaded_file.getbuffer())
        temp_path = temp_file.name

    try:

        # Upload and index the document
        operation = client.file_search_stores.upload_to_file_search_store(
            file=temp_path,
            file_search_store_name=store_name,
            config={
                "display_name": uploaded_file.name
            }
        )

        # Wait for indexing to finish
        while not operation.done:

            time.sleep(3)

            operation = client.operations.get(operation)

        if getattr(operation, "error", None):
            raise RuntimeError(str(operation.error))

        return uploaded_file.name

    finally:

        Path(temp_path).unlink(missing_ok=True)
