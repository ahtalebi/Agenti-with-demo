"""
Simple token storage and management.
"""
import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any

# Path to token database file
TOKEN_DB_PATH = "db/tokens.json"

def _ensure_db_exists():
    """Make sure the token database file exists."""
    os.makedirs(os.path.dirname(TOKEN_DB_PATH), exist_ok=True)
    if not os.path.exists(TOKEN_DB_PATH):
        with open(TOKEN_DB_PATH, "w") as f:
            json.dump([], f)

def _load_tokens() -> List[Dict[str, Any]]:
    """Load all tokens from database."""
    _ensure_db_exists()
    try:
        with open(TOKEN_DB_PATH, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def _save_tokens(tokens: List[Dict[str, Any]]):
    """Save tokens to database."""
    _ensure_db_exists()
    with open(TOKEN_DB_PATH, "w") as f:
        json.dump(tokens, f, default=str)

def create_token(customer_name: str, email: str) -> Dict[str, str]:
    """Create a new token for a customer."""
    token = str(uuid.uuid4())
    
    tokens = _load_tokens()
    tokens.append({
        "token": token,
        "customer_name": customer_name,
        "email": email,
        "created_at": datetime.now(),
        "status": "active"
    })
    
    _save_tokens(tokens)
    
    # Calculate the full URL (will be completed in routes.py)
    return {
        "token": token,
        "url": f"/demo?token={token}"
    }

def validate_token(token: str) -> bool:
    """Check if a token is valid."""
    tokens = _load_tokens()
    for t in tokens:
        if t["token"] == token and t["status"] == "active":
            return True
    return False

def revoke_token(token: str) -> bool:
    """Revoke a token."""
    tokens = _load_tokens()
    for t in tokens:
        if t["token"] == token:
            t["status"] = "revoked"
            _save_tokens(tokens)
            return True
    return False

def get_all_tokens() -> List[Dict[str, Any]]:
    """Get all tokens."""
    return _load_tokens()