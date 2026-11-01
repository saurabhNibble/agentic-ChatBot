import os
import json
import hashlib

from fastembed import TextEmbedding
from langchain_core.embeddings import Embeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(BASE_DIR, "faiss_index")
PDF_PATH = os.path.join(BASE_DIR, "set.pdf")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
REGISTRY_PATH = os.path.join(BASE_DIR, "indexed_files.json")


# 1. Local embeddings (no API key, runs inside the app)
class FastEmbeddings(Embeddings):
    def __init__(self, model_name="BAAI/bge-small-en-v1.5"):
        self.model = TextEmbedding(model_name=model_name)

    def embed_documents(self, texts):
        return [v.tolist() for v in self.model.embed(texts)]

    def embed_query(self, text):
        return next(iter(self.model.embed([text]))).tolist()


embeddings = FastEmbeddings()

# 2. Text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150
)


# 3. Load existing FAISS index
def load_vectorstore():
    if not os.path.exists(os.path.join(INDEX_PATH, "index.faiss")):
        return None

    return FAISS.load_local(
        INDEX_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )


# 4. Process a PDF file from disk
def process_pdf(file_path):
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    chunks = text_splitter.split_documents(documents)

    if not chunks:
        return "No readable text found in PDF."

    vectorstore = load_vectorstore()

    if vectorstore is None:
        vectorstore = FAISS.from_documents(chunks, embeddings)
    else:
        vectorstore.add_documents(chunks)

    vectorstore.save_local(INDEX_PATH)
    return f"Successfully indexed {len(chunks)} chunks."


# 5. Add an uploaded PDF (skips duplicates)
def add_uploaded_pdf(file_bytes, filename):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_hash = hashlib.sha256(file_bytes).hexdigest()

    registry = {}
    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH, "r") as f:
            registry = json.load(f)

    if file_hash in registry:
        return f"'{filename}' is already indexed."

    safe_name = os.path.basename(filename)
    path = os.path.join(UPLOAD_DIR, safe_name)

    with open(path, "wb") as f:
        f.write(file_bytes)

    result = process_pdf(path)

    if result.startswith("Successfully"):
        registry[file_hash] = safe_name
        with open(REGISTRY_PATH, "w") as f:
            json.dump(registry, f)

    return result


# 6. Search documents
def search_documents(query):
    vectorstore = load_vectorstore()

    if vectorstore is None:
        return []

    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    return retriever.invoke(query)


# 7. Build the index from set.pdf only if no index exists yet
def initialize_pdf():
    if os.path.exists(os.path.join(INDEX_PATH, "index.faiss")):
        print("Index already exists, skipping.")
        return

    if not os.path.exists(PDF_PATH):
        print("No set.pdf found. Waiting for uploads.")
        return

    print(process_pdf(PDF_PATH))


if __name__ == "__main__":
    test_vector = embeddings.embed_query("This is a test sentence.")
    print("Embedding successful!")
    print("Vector dimensions:", len(test_vector))  # should be 384

    initialize_pdf()