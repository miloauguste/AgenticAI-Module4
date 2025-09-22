"""
Agent State Management Module
Defines the state schema and state management for the customer support agent.
"""

from typing import Annotated, TypedDict, List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from langgraph.graph.message import add_messages


@dataclass
class UserHistoryEntry:
    """Represents a single entry in user's interaction history."""
    query: str
    resolution: str
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            'query': self.query,
            'resolution': self.resolution,
            'timestamp': self.timestamp,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserHistoryEntry':
        """Create from dictionary format."""
        return cls(
            query=data['query'],
            resolution=data['resolution'],
            timestamp=data['timestamp'],
            metadata=data.get('metadata', {})
        )


class AgentState(TypedDict):
    """
    Main state schema for the customer support agent.
    
    Attributes:
        messages: Short-term memory for current session messages
        user_history: Long-term memory for user's past interactions
        user_id: Unique identifier for the user
        thread_id: Unique identifier for the conversation thread
        metadata: Additional metadata for the session
        requires_hitl: Flag indicating if human intervention is needed
        hitl_approved: Flag indicating if HITL review was approved
    """
    messages: Annotated[List[Dict[str, Any]], add_messages]
    user_history: List[Dict[str, Any]]
    user_id: str
    thread_id: str
    metadata: Dict[str, Any]
    requires_hitl: bool
    hitl_approved: Optional[bool]


class StateValidator:
    """Validates AgentState fields to ensure data consistency."""
    
    @staticmethod
    def validate_state(state: AgentState) -> bool:
        """
        Validate the agent state structure and types.
        
        Args:
            state: The agent state to validate
            
        Returns:
            bool: True if valid, False otherwise
            
        Raises:
            ValueError: If validation fails with details
        """
        errors = []
        
        # Validate user_id
        if not isinstance(state.get('user_id', ''), str):
            errors.append("user_id must be a string")
        elif not state.get('user_id'):
            errors.append("user_id cannot be empty")
            
        # Validate thread_id
        if not isinstance(state.get('thread_id', ''), str):
            errors.append("thread_id must be a string")
        elif not state.get('thread_id'):
            errors.append("thread_id cannot be empty")
            
        # Validate messages
        if not isinstance(state.get('messages', []), list):
            errors.append("messages must be a list")
        else:
            for i, msg in enumerate(state.get('messages', [])):
                # Check if it's a LangChain Message object
                if hasattr(msg, 'type') and hasattr(msg, 'content'):
                    # Validate LangChain Message object
                    if not hasattr(msg, 'type') or not hasattr(msg, 'content'):
                        errors.append(f"Message at index {i} missing required attributes (type, content)")
                    elif msg.type not in ['human', 'ai', 'system']:
                        errors.append(f"Message at index {i} has invalid type: {msg.type}")
                    elif not isinstance(getattr(msg, 'content', ''), str):
                        errors.append(f"Message at index {i} content must be a string")
                elif isinstance(msg, dict):
                    # Legacy dictionary format validation for backward compatibility
                    if 'role' not in msg or 'content' not in msg:
                        errors.append(f"Message at index {i} missing required fields (role, content)")
                    elif msg['role'] not in ['user', 'assistant', 'system']:
                        errors.append(f"Message at index {i} has invalid role: {msg['role']}")
                else:
                    errors.append(f"Message at index {i} must be a LangChain Message object or dictionary")
                    
        # Validate user_history
        if not isinstance(state.get('user_history', []), list):
            errors.append("user_history must be a list")
        else:
            for i, entry in enumerate(state.get('user_history', [])):
                if not isinstance(entry, dict):
                    errors.append(f"History entry at index {i} must be a dictionary")
                else:
                    required_history_fields = ['query', 'resolution', 'timestamp']
                    for field in required_history_fields:
                        if field not in entry:
                            errors.append(f"History entry at index {i} missing required field: {field}")
                        elif not isinstance(entry[field], str):
                            errors.append(f"History entry at index {i} field '{field}' must be a string")
            
        # Validate metadata
        if not isinstance(state.get('metadata', {}), dict):
            errors.append("metadata must be a dictionary")
            
        # Validate HITL flags
        if not isinstance(state.get('requires_hitl', False), bool):
            errors.append("requires_hitl must be a boolean")
        
        # Validate hitl_approved (optional field)
        hitl_approved = state.get('hitl_approved')
        if hitl_approved is not None and not isinstance(hitl_approved, bool):
            errors.append("hitl_approved must be a boolean or None")
            
        if errors:
            raise ValueError(f"State validation failed: {'; '.join(errors)}")
            
        return True
    
    @staticmethod
    def validate_and_sanitize_state(state: AgentState) -> AgentState:
        """
        Validate and sanitize the agent state, fixing common issues.
        
        Args:
            state: The agent state to validate and sanitize
            
        Returns:
            AgentState: Sanitized state
            
        Raises:
            ValueError: If validation fails with unfixable issues
        """
        # Ensure required fields exist with defaults
        if 'messages' not in state:
            state['messages'] = []
        if 'user_history' not in state:
            state['user_history'] = []
        if 'metadata' not in state:
            state['metadata'] = {}
        if 'requires_hitl' not in state:
            state['requires_hitl'] = False
            
        # Ensure messages is a list
        if not isinstance(state['messages'], list):
            state['messages'] = []
            
        # Ensure user_history is a list
        if not isinstance(state['user_history'], list):
            state['user_history'] = []
            
        # Ensure metadata is a dict
        if not isinstance(state['metadata'], dict):
            state['metadata'] = {}
            
        # Now validate the sanitized state
        StateValidator.validate_state(state)
        
        return state
    
    @staticmethod
    def validate_message(message: Dict[str, Any]) -> bool:
        """Validate a single message structure."""
        required_fields = ['role', 'content']
        
        if not isinstance(message, dict):
            raise ValueError("Message must be a dictionary")
            
        for field in required_fields:
            if field not in message:
                raise ValueError(f"Message missing required field: {field}")
                
        if message['role'] not in ['user', 'assistant', 'system']:
            raise ValueError(f"Invalid role: {message['role']}")
            
        return True


def create_initial_state(user_id: str, thread_id: str) -> AgentState:
    """
    Create an initial agent state with given identifiers.
    
    Args:
        user_id: User identifier
        thread_id: Thread identifier
        
    Returns:
        AgentState: Initialized state
    """
    return AgentState(
        messages=[],
        user_history=[],
        user_id=user_id,
        thread_id=thread_id,
        metadata={
            'created_at': datetime.now().isoformat(),
            'session_count': 1
        },
        requires_hitl=False,
        hitl_approved=None
    )


def add_user_history_entry(
    state: AgentState,
    query: str,
    resolution: str,
    metadata: Optional[Dict[str, Any]] = None
) -> AgentState:
    """
    Add a new entry to user history.
    
    Args:
        state: Current agent state
        query: User query
        resolution: Resolution provided
        metadata: Optional metadata
        
    Returns:
        AgentState: Updated state
    """
    entry = UserHistoryEntry(
        query=query,
        resolution=resolution,
        timestamp=datetime.now().isoformat(),
        metadata=metadata or {}
    )
    
    # Ensure user_history is a list
    if 'user_history' not in state or not isinstance(state['user_history'], list):
        state['user_history'] = []
    
    state['user_history'].append(entry.to_dict())
    return state


def trim_messages(state: AgentState, max_messages: int = 5, preserve_system: bool = True) -> AgentState:
    """
    Trim messages to manage context window size with intelligent preservation.
    
    Args:
        state: Current agent state
        max_messages: Maximum number of messages to keep
        preserve_system: Whether to always preserve system messages
        
    Returns:
        AgentState: State with trimmed messages
    """
    if len(state['messages']) <= max_messages:
        return state
    
    messages = state['messages']
    
    # Separate system messages from others if preserving them
    if preserve_system:
        system_messages = [msg for msg in messages if hasattr(msg, 'type') and msg.type == 'system']
        non_system_messages = [msg for msg in messages if not (hasattr(msg, 'type') and msg.type == 'system')]
        
        # Keep recent non-system messages
        recent_messages = non_system_messages[-(max_messages - len(system_messages)):]
        
        # Combine system messages with recent messages
        state['messages'] = system_messages + recent_messages
    else:
        # Simple trimming - keep last max_messages
        state['messages'] = messages[-max_messages:]
    
    # Log trimming action
    if 'metadata' not in state:
        state['metadata'] = {}
    state['metadata']['messages_trimmed'] = len(messages) - len(state['messages'])
    state['metadata']['total_messages_before_trim'] = len(messages)
    
    return state


def filter_messages(state: AgentState, exclude_roles: List[str] = None, filter_config: Dict[str, Any] = None) -> AgentState:
    """
    Filter out irrelevant messages based on role, content, and configurable criteria.
    
    Args:
        state: Current agent state
        exclude_roles: List of roles to exclude
        filter_config: Configuration for filtering criteria
        
    Returns:
        AgentState: State with filtered messages
    """
    if exclude_roles is None:
        exclude_roles = []
    
    if filter_config is None:
        filter_config = {
            'filter_greetings': True,
            'filter_short_messages': True,
            'min_message_length': 10,
            'filter_repetitive': True,
            'filter_non_actionable': True,
            'preserve_important': True
        }
    
    original_count = len(state['messages'])
    filtered_messages = []
    
    # Define filtering criteria
    greeting_keywords = ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']
    farewell_keywords = ['bye', 'goodbye', 'see you', 'talk to you later', 'ttyl', 'farewell']
    non_actionable_keywords = ['ok', 'okay', 'thanks', 'thank you', 'got it', 'understood', 'sure', 'alright']
    important_keywords = ['password', 'reset', 'account', 'billing', 'refund', 'error', 'problem', 'issue', 'help', 'support']
    
    for msg in state['messages']:
        # Skip if role should be excluded
        if hasattr(msg, 'type') and msg.type in exclude_roles:
            continue
        
        content = getattr(msg, 'content', '').lower().strip()
        
        # Always preserve system messages and important messages
        if (hasattr(msg, 'type') and msg.type == 'system') or \
           (filter_config.get('preserve_important') and any(keyword in content for keyword in important_keywords)):
            filtered_messages.append(msg)
            continue
        
        # Filter short messages
        if filter_config.get('filter_short_messages') and len(content) < filter_config.get('min_message_length', 10):
            continue
        
        # Filter greetings
        if filter_config.get('filter_greetings') and any(keyword in content for keyword in greeting_keywords + farewell_keywords):
            continue
        
        # Filter non-actionable responses
        if filter_config.get('filter_non_actionable') and content in non_actionable_keywords:
            continue
        
        # Filter repetitive messages (check against last 3 messages)
        if filter_config.get('filter_repetitive'):
            recent_contents = [getattr(m, 'content', '').lower().strip() for m in filtered_messages[-3:]]
            if content in recent_contents:
                continue
        
        # Message passed all filters
        filtered_messages.append(msg)
    
    state['messages'] = filtered_messages
    
    # Log filtering action
    if 'metadata' not in state:
        state['metadata'] = {}
    state['metadata']['messages_filtered'] = original_count - len(filtered_messages)
    state['metadata']['total_messages_before_filter'] = original_count
    state['metadata']['filter_config_used'] = filter_config
    
    return state