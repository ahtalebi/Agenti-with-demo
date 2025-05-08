# In admin_auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import os

# Create security scheme
security = HTTPBasic(auto_error=True)  # Set auto_error to True

def get_admin_credentials():
    """Get admin credentials from environment or use defaults."""
    return {
        "username": os.getenv("ADMIN_USERNAME", "admin"),
        "password": os.getenv("ADMIN_PASSWORD", "!yZu2pYGP6%h#r*H")
    }

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify admin credentials securely."""
    # With auto_error=True, FastAPI will automatically handle cases where no credentials are provided
    
    admin_creds = get_admin_credentials()
    
    # Use constant-time comparison to prevent timing attacks
    correct_username = secrets.compare_digest(credentials.username, admin_creds["username"])
    correct_password = secrets.compare_digest(credentials.password, admin_creds["password"])
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    # If authentication passes, return the username
    return credentials.username