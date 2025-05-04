"""
Track user interactions with the chatbot.
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Any

# Path to interactions database file
INTERACTIONS_DB_PATH = "db/interactions.json"

def _ensure_db_exists():
    """Make sure the interactions database file exists."""
    os.makedirs(os.path.dirname(INTERACTIONS_DB_PATH), exist_ok=True)
    if not os.path.exists(INTERACTIONS_DB_PATH):
        with open(INTERACTIONS_DB_PATH, "w") as f:
            json.dump({}, f)

def _load_interactions() -> Dict[str, List[Dict[str, Any]]]:
    """Load all interactions from database."""
    _ensure_db_exists()
    try:
        with open(INTERACTIONS_DB_PATH, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def _save_interactions(interactions: Dict[str, List[Dict[str, Any]]]):
    """Save interactions to database."""
    _ensure_db_exists()
    with open(INTERACTIONS_DB_PATH, "w") as f:
        json.dump(interactions, f, default=str)

def record_interaction(token: str, question: str, answer: str):
    """Record a user interaction."""
    if not token:
        # Don't record interactions without a token
        return
    
    interactions = _load_interactions()
    
    # Initialize token history if not exists
    if token not in interactions:
        interactions[token] = []
    
    # Add the new interaction
    interactions[token].append({
        "timestamp": datetime.now(),
        "question": question,
        "answer": answer
    })
    
    _save_interactions(interactions)

def get_user_interactions(token: str) -> List[Dict[str, Any]]:
    """Get all interactions for a specific token."""
    interactions = _load_interactions()
    return interactions.get(token, [])

def get_all_interactions() -> Dict[str, List[Dict[str, Any]]]:
    """Get all interactions for all users."""
    return _load_interactions()

def get_interaction_stats() -> Dict[str, Any]:
    """Get statistics about interactions."""
    interactions = _load_interactions()
    
    total_users = len(interactions)
    total_interactions = sum(len(user_interactions) for user_interactions in interactions.values())
    
    users_stats = []
    for token, user_interactions in interactions.items():
        users_stats.append({
            "token": token[:8] + "...",  # Truncate for privacy
            "interaction_count": len(user_interactions),
            "last_activity": max(interaction["timestamp"] for interaction in user_interactions) if user_interactions else None
        })
    
    return {
        "total_users": total_users,
        "total_interactions": total_interactions,
        "users": users_stats
    }