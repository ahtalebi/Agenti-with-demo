"""
RAG (Retrieval-Augmented Generation) engine implementation.
"""
# Update these imports
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from .config import (OPENAI_API_KEY, MODEL_NAME, TEMPERATURE, 
                    DOCUMENT_PATH, DB_PATH, CHUNK_SIZE, CHUNK_OVERLAP,
                    OPENAI_BASE_URL)
from .document_processors import DocumentProcessor
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global QA chain instance
qa_chain = None


def initialize_qa_system():
    """Initialize the QA system with all documents in the data folder."""
    global qa_chain
    
    logger.info("Initializing RAG system...")
    logger.info(f"Using OpenAI base URL: {OPENAI_BASE_URL}")
    
    # Initialize document processor
    doc_processor = DocumentProcessor()
    
    # Get the data directory
    data_dir = os.path.dirname(DOCUMENT_PATH)
    if not data_dir:
        data_dir = "data"
    
    logger.info(f"Processing documents from: {data_dir}")
    
    # Check if data directory exists
    if not os.path.exists(data_dir):
        logger.error(f"Data directory '{data_dir}' does not exist!")
        return
    
    # List all files in the directory
    all_files = os.listdir(data_dir)
    logger.info(f"Found {len(all_files)} files in {data_dir}")
    
    # Process all documents in the data folder
    documents = doc_processor.process_directory(data_dir)
    
    # Log which files were successfully processed
    if documents:
        logger.info(f"Successfully processed {len(documents)} documents:")
        for doc in documents:
            logger.info(f"  ✓ {doc['filename']} ({doc['type']}) - {len(doc['content'])} characters")
    else:
        logger.warning("No documents could be processed!")
        # Create a dummy document to prevent errors
        documents = [{
            'filename': 'default.txt',
            'content': 'No documents available.',
            'type': '.txt',
            'path': 'default'
        }]
    
    # Initialize embeddings with custom OpenAI endpoint
    logger.info("Initializing OpenAI embeddings...")
    embeddings = OpenAIEmbeddings(
        openai_api_key=OPENAI_API_KEY,
        openai_api_base=OPENAI_BASE_URL
    )
    
    # Split documents into chunks
    logger.info("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    
    # Prepare texts and metadata for vector store
    texts = []
    metadatas = []
    
    for doc in documents:
        logger.info(f"Processing chunks for: {doc['filename']}")
        # Split document into chunks
        chunks = text_splitter.split_text(doc['content'])
        texts.extend(chunks)
        
        # Add metadata for each chunk
        for _ in chunks:
            metadatas.append({
                'source': doc['filename'],
                'type': doc['type']
            })
        
        logger.info(f"  Created {len(chunks)} chunks from {doc['filename']}")
    
    logger.info(f"Total chunks created: {len(texts)}")
    
    # Create vector store
    logger.info("Creating vector store...")
    vectorstore = Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas,
        persist_directory=DB_PATH
    )
    
    # Initialize chat model
    logger.info("Initializing chat model...")
    llm = ChatOpenAI(
        model_name=MODEL_NAME, 
        temperature=TEMPERATURE,
        openai_api_key=OPENAI_API_KEY,
        openai_api_base=OPENAI_BASE_URL
    )
    
    # Create QA chain
    logger.info("Creating QA chain...")
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        return_source_documents=True
    )
    
    logger.info("RAG system initialized successfully!")
    
    # Summary log
    logger.info("=== DOCUMENT PROCESSING SUMMARY ===")
    logger.info(f"Total files found: {len(all_files)}")
    logger.info(f"Successfully processed: {len(documents)}")
    logger.info(f"Total text chunks: {len(texts)}")
    logger.info("==================================")

def ask_question(question: str) -> str:
    """Ask a question using the RAG system."""
    global qa_chain
    
    if qa_chain is None:
        initialize_qa_system()
    
    try:
        logger.info(f"Received question: {question}")
        result = qa_chain({"query": question})
        
        # Get the answer
        answer = result["result"]
        
        # Optionally add source information
        if "source_documents" in result and result["source_documents"]:
            sources = set()
            for doc in result["source_documents"]:
                if "source" in doc.metadata:
                    sources.add(doc.metadata["source"])
            
            if sources:
                answer += f"\n\nSources: {', '.join(sources)}"
                logger.info(f"Answer sources: {', '.join(sources)}")
        
        return answer
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise Exception(f"Error processing your question: {str(e)}")