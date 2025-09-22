"""
Memory Management Module
Handles both short-term and long-term memory storage and retrieval.
"""

import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from langgraph.checkpoint.memory import MemorySaver


class MemoryManager:
    """Manages both short-term and long-term memory for the agent."""
    
    def __init__(self, storage_path: str = "./memory_storage"):
        """
        Initialize the memory manager.
        
        Args:
            storage_path: Path to store persistent memory
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.short_term_memory = MemorySaver()
        
    def get_user_file_path(self, user_id: str) -> Path:
        """Get the file path for a specific user's data."""
        return self.storage_path / f"user_{user_id}.json"
    
    def save_long_term_memory(
        self,
        user_id: str,
        user_history: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Save long-term memory to persistent storage.
        
        Args:
            user_id: User identifier
            user_history: List of historical interactions
            metadata: Additional metadata to store
            
        Returns:
            bool: Success status
        """
        try:
            file_path = self.get_user_file_path(user_id)
            
            data = {
                'user_id': user_id,
                'user_history': user_history,
                'metadata': metadata or {},
                'last_updated': datetime.now().isoformat()
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving long-term memory: {e}")
            return False
    
    def load_long_term_memory(self, user_id: str) -> Dict[str, Any]:
        """
        Load long-term memory from persistent storage.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict containing user history and metadata
        """
        file_path = self.get_user_file_path(user_id)
        
        if not file_path.exists():
            return {
                'user_id': user_id,
                'user_history': [],
                'metadata': {},
                'last_updated': None
            }
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"Error loading long-term memory: {e}")
            return {
                'user_id': user_id,
                'user_history': [],
                'metadata': {},
                'last_updated': None
            }
    
    def append_to_history(
        self,
        user_id: str,
        query: str,
        resolution: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Append a new interaction to user history with validation.
        
        Args:
            user_id: User identifier
            query: User's query
            resolution: Resolution provided
            metadata: Optional metadata
            
        Returns:
            bool: Success status
        """
        # Validate inputs
        if not isinstance(user_id, str) or not user_id.strip():
            print("Error: user_id must be a non-empty string")
            return False
        if not isinstance(query, str):
            print("Error: query must be a string")
            return False
        if not isinstance(resolution, str):
            print("Error: resolution must be a string")
            return False
        if metadata is not None and not isinstance(metadata, dict):
            print("Error: metadata must be a dictionary or None")
            return False
        
        data = self.load_long_term_memory(user_id)
        history = data.get('user_history', [])
        
        # Ensure history is a list
        if not isinstance(history, list):
            history = []
        
        new_entry = {
            'query': query,
            'resolution': resolution,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        history.append(new_entry)
        data['user_history'] = history
        
        return self.save_long_term_memory(user_id, history, data.get('metadata', {}))
    
    def clear_user_history(self, user_id: str) -> bool:
        """
        Clear all history for a specific user.
        
        Args:
            user_id: User identifier
            
        Returns:
            bool: Success status
        """
        file_path = self.get_user_file_path(user_id)
        
        try:
            if file_path.exists():
                file_path.unlink()
            return True
        except Exception as e:
            print(f"Error clearing user history: {e}")
            return False
    
    def get_checkpointer(self) -> MemorySaver:
        """
        Get the checkpointer for short-term memory.
        
        Returns:
            MemorySaver instance for state persistence
        """
        return self.short_term_memory

    def get_recent_history(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent history entries for a user."""
        try:
            data = self.load_long_term_memory(user_id)
            history = data.get('user_history', [])
            if not isinstance(history, list):
                history = []
            return history[-limit:] if len(history) > limit else history
        except Exception as e:
            print(f"Error getting recent history for user {user_id}: {e}")
            return []


class ExternalMemoryStore:
    """
    External memory store for scalable long-term memory.
    Can be extended to use databases like PostgreSQL, MongoDB, etc.
    """
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize external memory store.
        
        Args:
            connection_string: Database connection string
        """
        self.connection_string = connection_string
        self.in_memory_store = {}  # Fallback to in-memory storage
        
    def save(self, key: str, value: Dict[str, Any]) -> bool:
        """Save data to external store."""
        # This is a simplified implementation
        # In production, this would connect to a real database
        self.in_memory_store[key] = value
        return True
    
    def load(self, key: str) -> Optional[Dict[str, Any]]:
        """Load data from external store."""
        return self.in_memory_store.get(key)
    
    def delete(self, key: str) -> bool:
        """Delete data from external store."""
        if key in self.in_memory_store:
            del self.in_memory_store[key]
            return True
        return False
    
    def list_keys(self, prefix: str = "") -> List[str]:
        """List all keys with optional prefix."""
        if prefix:
            return [k for k in self.in_memory_store.keys() if k.startswith(prefix)]
        return list(self.in_memory_store.keys())
    
    def search_history(
        self,
        user_id: str,
        keyword: str
    ) -> List[Dict[str, Any]]:
        """
        Search user history for specific keywords with validation.
        
        Args:
            user_id: User identifier
            keyword: Keyword to search for
            
        Returns:
            List of matching history entries
        """
        # Validate inputs
        if not isinstance(user_id, str) or not user_id.strip():
            raise ValueError("user_id must be a non-empty string")
        if not isinstance(keyword, str) or not keyword.strip():
            raise ValueError("keyword must be a non-empty string")
        
        data = self.load_long_term_memory(user_id)
        history = data.get('user_history', [])
        
        # Validate history structure
        if not isinstance(history, list):
            print(f"Warning: Invalid history format for user {user_id}, returning empty results")
            return []
        
        keyword_lower = keyword.lower()
        matching_entries = []
        
        for entry in history:
            # Validate each entry structure
            if not isinstance(entry, dict):
                print(f"Warning: Skipping invalid history entry for user {user_id}")
                continue
                
            query = entry.get('query', '')
            resolution = entry.get('resolution', '')
            
            # Ensure query and resolution are strings
            if not isinstance(query, str):
                query = str(query) if query is not None else ''
            if not isinstance(resolution, str):
                resolution = str(resolution) if resolution is not None else ''
            
            # Check for keyword match
            if (keyword_lower in query.lower() or 
                keyword_lower in resolution.lower()):
                matching_entries.append(entry)
        
        return matching_entries
