import numpy as np
import json


def load_embeddings_from_file(file_name="embeddings.json"):
    """Load embeddings from a file."""
    embeddings = []
    content = []
    vec_indexs = []

    try:
        with open(file_name, "r") as file:
            # Read each line from the file
            for line in file:
                # Parse JSON data from the line
                data = json.loads(line)

                # Extract content, embeddings, and vec_indexs from the data
                content.append(data["content"])
                embeddings.append(data["embeddings"])
                vec_indexs.append(data["vec_indexes"])

        # Convert embeddings list to numpy array
        embeddings_array = np.array(embeddings)

        return content, embeddings_array, vec_indexs

    except FileNotFoundError:
        print(f"File not found: {file_name}")
        return None, None, None


def save_embeddings_to_file(
    content, embeddings, vec_indexes, file_name="embeddings.json"
):
    """Save the embeddings, content, and vec_indexes to a file."""
    # Convert numpy array to list for JSON serialization
    embeddings_list = embeddings.tolist()

    # Prepare data dictionary
    data = {
        "content": content,
        "embeddings": embeddings_list,
        "vec_indexes": vec_indexes,
    }

    # Write data to file
    with open(file_name, "a") as file:
        file.write(json.dumps(data) + "\n")
