import os
import PyPDF2
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# Specify the persistent storage path for ChromaDB
PERSISTENT_DB_PATH = "/Users/nuri/Documents/nr4a2_literature/rag_app/chroma/"

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
client = chromadb.PersistentClient(path=PERSISTENT_DB_PATH)

collection = client.get_or_create_collection("pdf_chunks")

# Function to read and chunk a PDF
def read_and_chunk_pdf(file_path, chunk_size=500):
    pdf_reader = PyPDF2.PdfReader(file_path)
    text_chunks = []
    doc_id = os.path.basename(file_path)

    for page_num, page in enumerate(pdf_reader.pages):
        text = page.extract_text()
        if text:
            # Split text into chunks of the given size
            words = text.split()
            for i in range(0, len(words), chunk_size):
                chunk_text = " ".join(words[i:i + chunk_size])
                chunk_metadata = {"doc_id": doc_id, "page_num": page_num, "chunk_idx": i // chunk_size}
                text_chunks.append((chunk_text, chunk_metadata))
    
    return text_chunks

# Function to generate embeddings
def generate_embeddings(chunks):
    texts = [chunk[0] for chunk in chunks]
    embeddings = embedding_model.encode(texts)
    return embeddings

# Function to check if a document already exists in the database
def document_exists(doc_id):
    results = collection.get(include=['metadatas'])
    existing_doc_ids = [doc['doc_id'] for doc in results['metadatas']]
    return doc_id in existing_doc_ids

# Function to store new chunks and embeddings in the database
def store_embeddings_in_chroma(chunks, embeddings):
    for i, (embedding, metadata) in enumerate(zip(embeddings, [chunk[1] for chunk in chunks])):
        collection.add(
            embeddings=[embedding.tolist()],
            metadatas=[metadata],
            ids=[f"{metadata['doc_id']}_chunk_{metadata['page_num']}_{metadata['chunk_idx']}"]
        )

# Function to process all PDFs in a folder
def process_pdfs_in_folder(folder_path, chunk_size=500):
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            doc_id = os.path.basename(file_path)
            
            # Skip if the document already exists in the database
            if document_exists(doc_id):
                print(f"Document '{doc_id}' already exists in the database. Skipping.")
                continue

            print(f"Processing document: {doc_id}")
            chunks = read_and_chunk_pdf(file_path, chunk_size)
            embeddings = generate_embeddings(chunks)
            store_embeddings_in_chroma(chunks, embeddings)
            print(f"Document '{doc_id}' processed and stored with {len(chunks)} chunks.")

# Example usage
if __name__ == "__main__":
    folder_path = "/Users/nuri/Documents/nr4a2_literature/rag_app/pdfs/"
    process_pdfs_in_folder(folder_path)
