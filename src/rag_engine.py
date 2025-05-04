"""
RAG (Retrieval-Augmented Generation) implementation.
"""
import os
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from src.config import (
    MODEL_NAME, 
    TEMPERATURE, 
    DOCUMENT_PATH, 
    DB_PATH, 
    CHUNK_SIZE, 
    CHUNK_OVERLAP,
    OPENAI_API_KEY,
    OPENAI_BASE_URL  # Import the new config variable
)

# Global variables for the QA system
qa_chain = None

def initialize_qa_system():
    """Initialize the QA system, loading or creating embeddings as needed."""
    global qa_chain
    
    # Only initialize once
    if qa_chain is not None:
        return qa_chain
    
    # Make sure the data directory exists
    os.makedirs(os.path.dirname(DOCUMENT_PATH), exist_ok=True)
    
    # Check if document exists
    if not os.path.exists(DOCUMENT_PATH):
    #    print(f"Warning: Document not found at {DOCUMENT_PATH}")
    #    print("Please place your document at this location before asking questions")
        # Create an empty file if it doesn't exist to prevent errors
        with open(DOCUMENT_PATH, 'w') as f:
            f.write("Example document. Replace with your actual content.")
    
    # Load the text file
    loader = TextLoader(DOCUMENT_PATH)
    documents = loader.load()

    # Split document into chunks for efficient retrieval
    text_splitter = CharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    chunks = text_splitter.split_documents(documents)
    
    # Check if we already have a persisted database
    if os.path.exists(DB_PATH):
#        print("Loading existing embeddings...")
        # Load existing vector store
#        embeddings = OpenAIEmbeddings()
        embeddings = OpenAIEmbeddings(
        openai_api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL  # Add custom base URL here too
        )
        vector_store = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
#        print("Embeddings loaded from disk")
    else:
#        print("Creating new embeddings...")
        # Create embeddings and store in vector database
        os.makedirs(DB_PATH, exist_ok=True)
#        embeddings = OpenAIEmbeddings()
        embeddings = OpenAIEmbeddings(
        openai_api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL  # Add custom base URL here too
        )
        vector_store = Chroma.from_documents(
            documents=chunks, 
            embedding=embeddings,
            persist_directory=DB_PATH
        )
#        print(f"Successfully embedded {len(chunks)} document chunks and saved to disk")
    
    # Create the retrieval QA chain
#    print("Setting up QA chain...")
    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(
            model=MODEL_NAME, 
            temperature=TEMPERATURE, 
            openai_api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL  # Add the custom base URL here
        ),
        chain_type="stuff",
        retriever=vector_store.as_retriever()
    )
#    print("QA chain ready!")
    return qa_chain

def ask_question(question):
    """Process a question and return the answer."""
    # Ensure the QA system is initialized
    global qa_chain
    if qa_chain is None:
        qa_chain = initialize_qa_system()
    
    # Use invoke instead of run to avoid deprecation warning
    response = qa_chain.invoke({"query": question})
    return response["result"]
