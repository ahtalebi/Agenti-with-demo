"""
Main entry point for the RAG Server application.
"""
import os
import uvicorn
from dotenv import load_dotenv
from src.rag_engine import initialize_qa_system

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Initialize the QA system before starting server
    print("Initializing QA system...")
    initialize_qa_system()

    PORT = int(os.getenv("PORT", 8000))
    HOST = os.getenv("HOST", "0.0.0.0")
    BASE_URL = os.getenv("BASE_URL", "https://chatbot.finitx.com")
    
    print(f"\nStarting server on {HOST}:{PORT}")
    print(f"Access the API documentation at {BASE_URL}/docs")
    print(f"Access the admin panel at {BASE_URL}/admin.html")
    
    # Run the server
    uvicorn.run("app:app", host=HOST, port=PORT, reload=True)