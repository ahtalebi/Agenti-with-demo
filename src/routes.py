"""
API routes for the application.
"""
from src.models import QuestionRequest, AnswerResponse, HealthResponse
from src.rag_engine import ask_question
from src.token_store import create_token, revoke_token, get_all_tokens, validate_token
from src.models import Token, TokenResponse, InteractionStatsResponse
from src.interaction_tracker import record_interaction, get_user_interactions, get_interaction_stats
from src.admin_auth import verify_admin
from fastapi import APIRouter, HTTPException, Form, Depends, Request
from typing import List, Dict
import os
import mimetypes
from pathlib import Path
from fastapi import HTTPException



# Create routers
router = APIRouter(prefix="/api", tags=["RAG Chatbot"])
admin_router = APIRouter(prefix="/api/token", tags=["Token Management"])
interaction_router = APIRouter(prefix="/api/interactions", tags=["User Interactions"])

# Main API endpoints
@router.post("/ask", response_model=AnswerResponse)
async def ask_endpoint(req: QuestionRequest, request: Request):
    """API endpoint to ask questions about the document."""
    if not req.question or req.question.strip() == "":
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        # Get token from request
        token = request.query_params.get("token")
        if not token:
            token = request.cookies.get("auth_token")
            
        # Get answer
        answer = ask_question(req.question)
        
        # Record interaction
        record_interaction(token, req.question, answer)
        
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint to verify the API is running."""
    return {"status": "ok"}

# Token management endpoints - now with admin authentication
@admin_router.post("/create", response_model=TokenResponse)
async def generate_token(
    customer_name: str = Form(...), 
    email: str = Form(...),
    admin_user: str = Depends(verify_admin)
):
    """Generate a new access token. Requires admin authentication."""
    token_data = create_token(customer_name, email)
    # Get base URL from a config or environment variable
    base_url = "http://localhost:8000"  # Change this to your actual domain
    token_data["url"] = f"{base_url}/demo?token={token_data['token']}"
    return token_data

@admin_router.post("/revoke")
async def revoke_token_endpoint(
    token: str = Form(...),
    admin_user: str = Depends(verify_admin)
):
    """Revoke an access token. Requires admin authentication."""
    if revoke_token(token):
        return {"status": "success", "message": "Token revoked successfully"}
    raise HTTPException(status_code=404, detail="Token not found")

@admin_router.get("/list", response_model=List[Token])
async def list_tokens(admin_user: str = Depends(verify_admin)):
    """List all tokens. Requires admin authentication."""
    return get_all_tokens()

@admin_router.get("/validate")
async def validate_token_endpoint(token: str):
    """Validate a token."""
    if validate_token(token):
        return {"valid": True}
    return {"valid": False}

# User interaction endpoints
@interaction_router.get("/stats", response_model=InteractionStatsResponse)
async def get_stats(admin_user: str = Depends(verify_admin)):
    """Get interaction statistics. Requires admin authentication."""
    return get_interaction_stats()

@interaction_router.get("/user/{token}", response_model=Dict)
async def get_user_history(token: str, admin_user: str = Depends(verify_admin)):
    """Get interaction history for a specific user. Requires admin authentication."""
    interactions = get_user_interactions(token)
    return {"token": token, "interactions": interactions}


@interaction_router.get("/count")
async def get_interaction_count(token: str):
    """Get the count of interactions for a specific token."""
    if not token:
        return {"count": 0}
    
    interactions = get_user_interactions(token)
    return {"count": len(interactions)}



@admin_router.get("/info")
async def get_token_info(token: str):
    """Get customer information for a token without requiring admin authentication."""
    try:
        print(f"[DEBUG] Token info requested for: '{token}'")
        
        # Get all tokens
        all_tokens = get_all_tokens()
        print(f"[DEBUG] Found {len(all_tokens)} tokens in database")
        
        # Find the matching token - modified to work with dict objects
        for t in all_tokens:
            # Check if t is a dict
            if isinstance(t, dict):
                if t.get('token') == token:
                    print(f"[DEBUG] Token MATCH found for dict! Returning info for: {t.get('customer_name')}")
                    return {
                        "customer_name": t.get('customer_name', ''),
                        "email": t.get('email', '')
                    }
            # Handle Token objects (original approach)
            elif hasattr(t, 'token'):
                if t.token == token:
                    print(f"[DEBUG] Token MATCH found for object! Returning info for: {t.customer_name}")
                    return {
                        "customer_name": t.customer_name,
                        "email": t.email
                    }
        
        # If token not found, return empty data instead of an error
        print(f"[DEBUG] No match found for token: '{token}'")
        return {"customer_name": "", "email": ""}
    except Exception as e:
        # Log the error but return a graceful response
        print(f"[DEBUG] Error retrieving token info: {str(e)}")
        return {"customer_name": "", "email": ""}








@router.get("/documents")  # Note: router already has "/api" prefix
async def get_documents():
    """Get a list of all documents in the data folder."""
    try:
        data_dir = "data"
        documents = []
        
        if not os.path.exists(data_dir):
            return {"documents": []}
            
        for file_name in os.listdir(data_dir):
            file_path = os.path.join(data_dir, file_name)
            
            # Skip directories and hidden files
            if os.path.isdir(file_path) or file_name.startswith('.'):
                continue
            
            # Get file size in KB
            size_bytes = os.path.getsize(file_path)
            size_kb = size_bytes / 1024
            
            if size_kb < 1024:
                size_str = f"{size_kb:.0f} KB"
            else:
                size_mb = size_kb / 1024
                size_str = f"{size_mb:.1f} MB"
            
            # Determine file type
            mime_type = mimetypes.guess_type(file_path)[0]
            file_type = "unknown"
            
            if mime_type:
                if "pdf" in mime_type:
                    file_type = "pdf"
                elif "excel" in mime_type or "spreadsheet" in mime_type:
                    file_type = "excel"
                elif "word" in mime_type or "document" in mime_type:
                    file_type = "word"
                elif "text" in mime_type:
                    file_type = "text"
            
            # Default to file extension if MIME type doesn't match
            if file_type == "unknown":
                ext = os.path.splitext(file_path)[1].lower()
                if ext == ".pdf":
                    file_type = "pdf"
                elif ext in [".xls", ".xlsx", ".csv"]:
                    file_type = "excel"
                elif ext in [".doc", ".docx"]:
                    file_type = "word"
                elif ext in [".txt", ".md"]:
                    file_type = "text"
            
            # Create ID from filename (remove extension, replace spaces with hyphens)
            file_id = os.path.splitext(file_name)[0].lower().replace(" ", "-").replace("_", "-")
            
            # Create a title from filename (replace underscores with spaces, capitalize)
            title = os.path.splitext(file_name)[0].replace("_", " ").title()
            
            # Generate a simple description based on the title
            description = f"{title} document for reference."
            
            document = {
                "id": file_id,
                "title": title,
                "filename": file_name,
                "description": description,
                "size": size_str,
                "type": file_type
            }
            
            documents.append(document)
            
        return {"documents": documents}
    except Exception as e:
        print(f"Error listing documents: {str(e)}")  # Log the error
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")