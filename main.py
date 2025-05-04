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
    HOST = os.getenv("HOST", "localhost")
    
    print(f"\nStarting server on http://{HOST}:{PORT}")
    print(f"Access the API documentation at http://{HOST}:{PORT}/docs")
    print(f"Access the admin panel at http://{HOST}:{PORT}/admin.html")
    print(f"Access from other devices using your computer's IP address")
    print(f"Try: http://YOUR_IP_ADDRESS:{PORT}")
    
    # Run the server
    uvicorn.run("app:app", host=HOST, port=PORT, reload=True)