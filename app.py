"""
FastAPI application setup.
"""
import os
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials

# Import the admin_auth module explicitly
from src.admin_auth import verify_admin

from src.routes import router, admin_router, interaction_router
from src.rag_engine import initialize_qa_system
from contextlib import asynccontextmanager
from src.token_store import validate_token

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for the FastAPI app.
    Initializes QA system on startup.
    """
    # Initialize QA system on startup
    initialize_qa_system()
    yield
    # You could add cleanup here if needed

# Create FastAPI app with lifespan management
app = FastAPI(
    title="RAG Chatbot API",
    description="API for a Retrieval-Augmented Generation chatbot",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware for authentication
@app.middleware("http")
async def validate_token_middleware(request: Request, call_next):
    """Check if the request has a valid token for protected paths."""
    path = request.url.path
    
    # Handle direct access to admin.html by redirecting to /admin
    #if path == "/admin.html":
     #   return RedirectResponse(url="/admin")
    
    # Skip authentication for these paths
    skip_auth_paths = [
        "/admin",                     # Admin entry point (will be authenticated by its route handler)
        "/api/token/",                # Token management APIs (already have auth in routes)
        "/api/interactions/",         # Interaction statistics APIs (already have auth in routes)
       # "/docs",                      # API docs
        "/openapi.json",              # OpenAPI schema
        "/static/",                   # Static files
        "/access-denied.html",        # Access denied page
        "/api/health",

    ]
    
    # Check if path should skip authentication
    for skip_path in skip_auth_paths:
        if path == skip_path or (skip_path.endswith('/') and path.startswith(skip_path)):
            return await call_next(request)
    
    # Skip authentication for static file extensions (except HTML)
    if path.endswith((".css", ".js", ".png", ".jpg", ".ico")) and not path.endswith(".html"):
        return await call_next(request)
    
    # Check token for everything else
    token = request.query_params.get("token")
    
    # If token is not in query params, check the cookies
    if not token:
        token = request.cookies.get("auth_token")
    
    if not token or not validate_token(token):
        if path.startswith("/api/"):
            raise HTTPException(status_code=401, detail="Unauthorized")
        else:
            return RedirectResponse(url="/access-denied.html")
    
    # If token is valid, proceed with the request
    response = await call_next(request)
    
    # Add token to cookies if not already there
    if token and not request.cookies.get("auth_token"):
        response.set_cookie(key="auth_token", value=token, httponly=True)
    
    return response

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)
app.include_router(admin_router)
app.include_router(interaction_router)

# Route for admin panel with auth
@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(admin_user: str = Depends(verify_admin)):
    """Serve admin panel with admin authentication."""
    try:
        with open("protected_templates/admin.html", "r") as file:
            content = file.read()
        return HTMLResponse(content=content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error serving admin page: {str(e)}")



@app.get("/admin.html", response_class=HTMLResponse)
async def admin_html_panel(admin_user: str = Depends(verify_admin)):
    """Serve admin panel with admin authentication."""
    return RedirectResponse(url="/admin")


# Route for access-denied page
@app.get("/access-denied.html", response_class=HTMLResponse)
async def access_denied_page():
    """Serve the access denied page."""
    try:
        with open("static/access-denied.html", "r") as file:
            content = file.read()
        return HTMLResponse(content=content)
    except Exception as e:
        # Fallback if file not found
        html_content = """<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Access Denied</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                    text-align: center;
                }
                .container {
                    background-color: white;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                    padding: 40px;
                    margin-top: 50px;
                }
                h1 {
                    color: #d32f2f;
                }
                p {
                    font-size: 18px;
                    line-height: 1.6;
                }
                .icon {
                    font-size: 72px;
                    color: #d32f2f;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="icon">⛔</div>
                <h1>Access Denied</h1>
                <p>You do not have permission to access this page.</p>
                <p>Please contact the administrator to request access.</p>
            </div>
        </body>
        </html>"""
        return HTMLResponse(content=html_content)

@app.get("/debug-auth")
async def debug_auth(credentials: HTTPBasicCredentials = Depends(HTTPBasic())):
    """Debug endpoint for auth testing."""
    return {
        "username": credentials.username,
        "password_length": len(credentials.password),
        "auth_successful": True
    }

@app.get("/demo", response_class=HTMLResponse)
async def demo_page(request: Request):
    """Demo page with token validation."""
    token = request.query_params.get("token")
    
    if not token or not validate_token(token):
        return RedirectResponse(url="/access-denied.html")
    
    # If token is valid, serve the demo page
    with open("static/demo.html", "r") as file:
        content = file.read()
    return HTMLResponse(content=content)

@app.get("/", response_class=HTMLResponse)
async def index_page():
    """Serve the index page."""
    try:
        with open("static/index.html", "r") as file:
            content = file.read()
        return HTMLResponse(content=content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error serving index page: {str(e)}")




# Mount the data directory to make files accessible
try:
    # Create the data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    app.mount("/data", StaticFiles(directory="data"), name="data")
except Exception as e:
    print(f"Warning: Could not mount data files: {str(e)}")


# Mount static files - IMPORTANT: Mount this AFTER defining all the routes!
# Mount the static files for CSS, JS, images, etc. (but not HTML files)
try:
    # Create the static directory if it doesn't exist
    os.makedirs("static", exist_ok=True)
    app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception as e:
    print(f"Warning: Could not mount static files: {str(e)}")