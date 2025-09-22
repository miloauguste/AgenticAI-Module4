"""
Main Application Module
Entry point for the Customer Support Agent with LangGraph.
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage

from agent_state import create_initial_state, StateValidator
from memory_manager import MemoryManager
from graph_builder import AgentGraphBuilder


class CustomerSupportAgent:
    """Main customer support agent class."""
    
    def __init__(self, storage_path: str = "./memory_storage"):
        """
        Initialize the customer support agent.
        
        Args:
            storage_path: Path for memory storage
        """
        # Load environment variables
        load_dotenv()
        
        # Initialize components
        self.memory_manager = MemoryManager(storage_path)
        self.graph_builder = AgentGraphBuilder(self.memory_manager)
        self.agent = self.graph_builder.compile_graph()
        self.validator = StateValidator()
        
    def start_session(self, user_id: str, thread_id: str) -> Dict[str, Any]:
        """
        Start a new support session.
        
        Args:
            user_id: Unique user identifier
            thread_id: Unique thread identifier
            
        Returns:
            Initial session info
        """
        # Create initial state
        state = create_initial_state(user_id, thread_id)
        
        # Validate and sanitize state
        state = self.validator.validate_and_sanitize_state(state)
        
        # Load user history
        history_data = self.memory_manager.load_long_term_memory(user_id)
        state['user_history'] = history_data.get('user_history', [])
        
        return {
            'session_id': f"{user_id}_{thread_id}",
            'user_id': user_id,
            'thread_id': thread_id,
            'history_count': len(state['user_history']),
            'status': 'active'
        }
    
    def process_message(
        self,
        user_id: str,
        thread_id: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Process a user message and generate response.
        
        Args:
            user_id: User identifier
            thread_id: Thread identifier
            message: User's message
            
        Returns:
            Response data
        """
        # Create or load state
        config = {
            "configurable": {
                "thread_id": thread_id,
                "user_id": user_id
            }
        }
        
        # Create initial state
        state = create_initial_state(user_id, thread_id)
        
        # Add user message
        user_message = HumanMessage(content=message)
        
        state['messages'].append(user_message)
        
        # Process through graph
        result = self.agent.invoke(state, config)
        
        # Extract response
        response_message = None
        for msg in reversed(result['messages']):
            if hasattr(msg, 'type') and msg.type == 'ai':
                response_message = msg
                break
        
        return {
            'response': getattr(response_message, 'content', '') if response_message else 'I apologize, but I encountered an issue processing your request.',
            'requires_hitl': result.get('requires_hitl', False),
            'metadata': result.get('metadata', {}),
            'session_id': f"{user_id}_{thread_id}"
        }
    
    def get_user_history(self, user_id: str, limit: int = 10) -> list:
        """
        Get user's interaction history.
        
        Args:
            user_id: User identifier
            limit: Maximum number of entries
            
        Returns:
            List of history entries
        """
        return self.memory_manager.get_recent_history(user_id, limit)
    
    def approve_hitl(
        self,
        user_id: str,
        thread_id: str,
        approved: bool,
        feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Approve or reject HITL escalation.
        
        Args:
            user_id: User identifier
            thread_id: Thread identifier
            approved: Approval status
            feedback: Optional feedback
            
        Returns:
            Update status
        """
        config = {
            "configurable": {
                "thread_id": thread_id,
                "user_id": user_id
            }
        }
        
        # Update state with approval
        state = create_initial_state(user_id, thread_id)
        state['hitl_approved'] = approved
        
        if approved:
            message = f"Your issue has been reviewed and approved. {feedback if feedback else 'Our team will contact you with the resolution.'}"
        else:
            message = f"Your issue has been reviewed. {feedback if feedback else 'Our team will follow up with alternative solutions.'}"
        
        state['messages'].append(AIMessage(content=message))
        
        return {
            'status': 'approved' if approved else 'rejected',
            'message': message,
            'session_id': f"{user_id}_{thread_id}"
        }


def main():
    """Main entry point for CLI usage."""
    print("=" * 60)
    print("TechTrend Innovations - Customer Support Agent")
    print("Powered by LangGraph")
    print("=" * 60)
    print()
    
    agent = CustomerSupportAgent()
    
    # Get user credentials
    user_id = input("Enter User ID: ").strip()
    thread_id = input("Enter Thread ID: ").strip()
    
    if not user_id or not thread_id:
        print("Error: User ID and Thread ID are required.")
        return
    
    # Start session
    session_info = agent.start_session(user_id, thread_id)
    print(f"\nSession started successfully!")
    print(f"Session ID: {session_info['session_id']}")
    print(f"Previous interactions: {session_info['history_count']}")
    print()
    
    # Chat loop
    print("Type 'quit' to exit, 'history' to view history, 'clear' to start fresh")
    print("-" * 60)
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() == 'quit':
            print("\nThank you for using TechTrend Support. Goodbye!")
            break
        
        if user_input.lower() == 'history':
            history = agent.get_user_history(user_id, limit=5)
            print("\n--- Recent History ---")
            for idx, entry in enumerate(history, 1):
                print(f"{idx}. Query: {entry['query']}")
                print(f"   Resolution: {entry['resolution'][:100]}...")
                print()
            continue
        
        if user_input.lower() == 'clear':
            agent.memory_manager.clear_user_history(user_id)
            print("History cleared.")
            continue
        
        # Process message
        result = agent.process_message(user_id, thread_id, user_input)
        
        print(f"\nAgent: {result['response']}")
        
        if result['requires_hitl']:
            print("\n[!] This query has been escalated for human review.")
            approval = input("Approve resolution? (y/n): ").strip().lower()
            
            if approval == 'y':
                feedback = input("Enter feedback (optional): ").strip()
                approval_result = agent.approve_hitl(
                    user_id,
                    thread_id,
                    True,
                    feedback if feedback else None
                )
                print(f"\n{approval_result['message']}")


if __name__ == "__main__":
    main()