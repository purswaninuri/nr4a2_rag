import streamlit as st
import openai
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import openai
from openai import OpenAI
import os

# Initialize OpenAI API key

client2 = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Specify the persistent storage path for ChromaDB
PERSISTENT_DB_PATH = "./chroma/"

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
client = chromadb.PersistentClient(path=PERSISTENT_DB_PATH)

collection = client.get_collection("pdf_chunks")


def retrieve_relevant_chunks(query, top_k=3):
    query_embedding = embedding_model.encode([query])[0].tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    
    # Extract the necessary information from results
    ids = results['ids'][0]  # List of document IDs
    metadatas = results['metadatas'][0]  # List of metadata entries

    chunks = []
    for i, metadata in enumerate(metadatas):
        doc_id = metadata.get('doc_id', 'Unknown')
        page_num = metadata.get('page_num', 'Unknown')
        chunk_text = f"{doc_id} (Page {page_num})"
        chunks.append(chunk_text)

    return chunks


# Function to summarize retrieved chunks using OpenAI
def summarize_chunks(chunks):
    combined_text = "\n".join(chunks)

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "system", "content": f"Context: {combined_text}"},
        {"role": "user", "content": query}
    ]

   # Query OpenAI's ChatCompletion API
    response = client2.chat.completions.create(model="gpt-3.5-turbo", messages=messages)

    answer = response.choices[0].message.content
    return answer


# Streamlit UI
st.title("Document Query & Summarization App")
st.write("This app allows you to query documents and receive summarized results.")

query = st.text_input("Enter your query:")

if st.button("Search & Summarize") and query:
    with st.spinner("Retrieving relevant information..."):
        chunks = retrieve_relevant_chunks(query)
        if chunks:
            st.write("Retrieved Chunks:")
            for chunk in chunks:
                st.write(chunk)
            
            with st.spinner("Summarizing..."):
                summary = summarize_chunks(chunks)
                st.subheader("Summary:")
                st.write(summary)
        else:
            st.write("No relevant information found.")
