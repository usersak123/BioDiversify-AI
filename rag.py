import os
import glob
import chromadb

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()


# ============================================================
# 1. EMBEDDING MODEL
# ============================================================

print("Loading embedding model...")

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("Embedding model loaded.")


# ============================================================
# 2. CHROMADB
# ============================================================

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_or_create_collection(
    name="biodiversity_knowledge"
)


# ============================================================
# 3. LOAD DOCUMENTS
# ============================================================

def load_documents():

    documents = []
    ids = []
    metadatas = []

    files = glob.glob("data/*.txt")

    print(f"Found {len(files)} knowledge files.")

    for file_path in files:

        filename = os.path.basename(file_path)

        category = filename.replace(
            ".txt", ""
        )

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as f:

            text = f.read()

        # ----------------------------------------------------
        # Split into smaller chunks
        # ----------------------------------------------------

        chunks = [
            text[i:i + 1000]
            for i in range(
                0,
                len(text),
                1000
            )
        ]

        for index, chunk in enumerate(chunks):

            # Ignore extremely small chunks
            if len(chunk.strip()) < 50:
                continue

            documents.append(
                chunk.strip()
            )

            ids.append(
                f"{category}_{index}"
            )

            metadatas.append({

                "source": category,

                "file": filename,

                "chunk": index,

                "type": (
                    "intervention"
                    if category == "interventions"
                    else "scientific_knowledge"
                )
            })

    return (
        documents,
        ids,
        metadatas
    )


# ============================================================
# 4. BUILD KNOWLEDGE BASE
# ============================================================

def build_knowledge_base():

    documents, ids, metadatas = load_documents()

    if not documents:

        print(
            "No documents found in data/ folder."
        )

        return

    print(
        f"Preparing {len(documents)} chunks..."
    )

    # --------------------------------------------------------
    # IMPORTANT:
    # Delete old collection so new knowledge is indexed.
    # --------------------------------------------------------

    global collection

    try:

        client.delete_collection(
            name="biodiversity_knowledge"
        )

    except Exception:

        pass

    collection = client.get_or_create_collection(
        name="biodiversity_knowledge"
    )

    # --------------------------------------------------------
    # Generate embeddings
    # --------------------------------------------------------

    print(
        "Generating embeddings..."
    )

    embeddings = embedding_model.encode(
        documents,
        show_progress_bar=True
    ).tolist()

    # --------------------------------------------------------
    # Add to ChromaDB
    # --------------------------------------------------------

    collection.add(

        documents=documents,

        embeddings=embeddings,

        ids=ids,

        metadatas=metadatas
    )

    print(
        f"Knowledge base created with "
        f"{len(documents)} chunks."
    )


# ============================================================
# 5. RETRIEVE KNOWLEDGE
# ============================================================

def retrieve_knowledge(
    query,
    n_results=5
):

    # --------------------------------------------------------
    # Convert query into embedding
    # --------------------------------------------------------

    query_embedding = embedding_model.encode(
        [query]
    ).tolist()

    # --------------------------------------------------------
    # Search ChromaDB
    # --------------------------------------------------------

    results = collection.query(

        query_embeddings=query_embedding,

        n_results=n_results
    )

    documents = results["documents"][0]

    metadatas = results["metadatas"][0]

    # --------------------------------------------------------
    # Return document + metadata
    # --------------------------------------------------------

    return list(
        zip(
            documents,
            metadatas
        )
    )


# ============================================================
# 6. TEST RETRIEVAL
# ============================================================

if __name__ == "__main__":

    print("\nBuilding biodiversity knowledge base...\n")

    build_knowledge_base()

    print("\nTesting retrieval...\n")

    test_query = (
        "How can biodiversity be improved "
        "when soil organic carbon is low, "
        "rainfall is low and land is under monoculture?"
    )

    results = retrieve_knowledge(
        test_query,
        n_results=5
    )

    print(
        f"\nRetrieved {len(results)} results:\n"
    )

    for i, (document, metadata) in enumerate(
        results,
        start=1
    ):

        print(
            f"\n{'=' * 60}"
        )

        print(
            f"RESULT {i}"
        )

        print(
            f"Metadata: {metadata}"
        )

        print(
            f"\n{document[:1000]}"
        )