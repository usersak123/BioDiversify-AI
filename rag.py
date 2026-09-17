import os
import glob
import chromadb

from sentence_transformers import SentenceTransformer


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

CHROMA_DIR = os.path.join(
    BASE_DIR,
    "chroma_db"
)


# ============================================================
# EMBEDDING MODEL
# ============================================================

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ============================================================
# CHROMADB
# ============================================================

client = chromadb.PersistentClient(
    path=CHROMA_DIR
)

collection = client.get_or_create_collection(
    name="biodiversity_knowledge"
)


# ============================================================
# LOAD DOCUMENTS
# ============================================================

def load_documents():

    documents = []
    ids = []
    metadatas = []

    files = glob.glob(
        os.path.join(
            DATA_DIR,
            "*.txt"
        )
    )

    for file_path in files:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as f:

            text = f.read()

        # ----------------------------------------------------
        # Chunk text
        # ----------------------------------------------------

        chunks = [
            text[i:i + 1000]
            for i in range(
                0,
                len(text),
                1000
            )
        ]

        filename = os.path.basename(
            file_path
        )

        category = os.path.splitext(
            filename
        )[0]

        # ----------------------------------------------------
        # Store chunks
        # ----------------------------------------------------

        for index, chunk in enumerate(chunks):

            if not chunk.strip():
                continue

            documents.append(
                chunk
            )

            ids.append(
                f"{category}_{index}"
            )

            metadatas.append({

                "source": category,

                "file": filename,

                "type": "scientific_knowledge"

            })

    return (
        documents,
        ids,
        metadatas
    )


# ============================================================
# BUILD KNOWLEDGE BASE
# ============================================================

def build_knowledge_base():

    documents, ids, metadatas = (
        load_documents()
    )

    if not documents:

        print(
            "No knowledge files found."
        )

        return

    # --------------------------------------------------------
    # Avoid duplicate insertion
    # --------------------------------------------------------

    existing_ids = set()

    try:

        existing = collection.get()

        if existing and existing.get("ids"):

            existing_ids = set(
                existing["ids"]
            )

    except Exception:

        pass

    # --------------------------------------------------------
    # Add only new documents
    # --------------------------------------------------------

    new_documents = []
    new_ids = []
    new_metadatas = []

    for document, doc_id, metadata in zip(
        documents,
        ids,
        metadatas
    ):

        if doc_id not in existing_ids:

            new_documents.append(
                document
            )

            new_ids.append(
                doc_id
            )

            new_metadatas.append(
                metadata
            )

    if not new_documents:

        print(
            f"Knowledge base already contains "
            f"{collection.count()} chunks."
        )

        return

    # --------------------------------------------------------
    # Generate embeddings
    # --------------------------------------------------------

    embeddings = embedding_model.encode(
        new_documents,
        show_progress_bar=False
    ).tolist()

    # --------------------------------------------------------
    # Store in ChromaDB
    # --------------------------------------------------------

    collection.add(

        documents=new_documents,

        embeddings=embeddings,

        ids=new_ids,

        metadatas=new_metadatas

    )

    print(
        f"Added {len(new_documents)} new chunks."
    )

    print(
        f"Total knowledge chunks: "
        f"{collection.count()}"
    )


# ============================================================
# RETRIEVE KNOWLEDGE
# ============================================================

def retrieve_knowledge(
    query,
    n_results=5
):

    # --------------------------------------------------------
    # Make sure knowledge base exists
    # --------------------------------------------------------

    if collection.count() == 0:

        build_knowledge_base()

    # --------------------------------------------------------
    # Query embedding
    # --------------------------------------------------------

    query_embedding = (
        embedding_model
        .encode(
            [query]
        )
        .tolist()
    )

    # --------------------------------------------------------
    # Chroma search
    # --------------------------------------------------------

    results = collection.query(

        query_embeddings=query_embedding,

        n_results=n_results

    )

    documents = (
        results.get(
            "documents",
            [[]]
        )[0]
    )

    metadatas = (
        results.get(
            "metadatas",
            [[]]
        )[0]
    )

    return list(
        zip(
            documents,
            metadatas
        )
    )