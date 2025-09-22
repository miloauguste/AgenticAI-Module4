"""
Graph Builder Module
Constructs the LangGraph state graph for the customer support agent.
"""

from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage

from agent_state import AgentState, trim_messages, filter_messages, add_user_history_entry
from query_processor import QueryProcessor, ResponseFormatter
from memory_manager import MemoryManager


class AgentGraphBuilder:
    """Builds and configures the LangGraph agent."""
    
    def __init__(self, memory_manager: MemoryManager):
        """
        Initialize the graph builder.
        
        Args:
            memory_manager: Memory manager instance
        """
        self.memory_manager = memory_manager
        self.query_processor = QueryProcessor()
        self.response_formatter = ResponseFormatter()
        
    def build_graph(self) -> StateGraph:
        """
        Build the state graph for the agent.
        
        Returns:
            Configured StateGraph instance
        """
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("process_query", self.process_query_node)
        workflow.add_node("fetch_history", self.fetch_history_node)
        workflow.add_node("generate_response", self.generate_response_node)
        workflow.add_node("check_hitl", self.check_hitl_node)
        workflow.add_node("save_interaction", self.save_interaction_node)
        workflow.add_node("trim_state", self.trim_state_node)
        
        # Set entry point
        workflow.set_entry_point("fetch_history")
        
        # Add edges
        workflow.add_edge("fetch_history", "process_query")
        workflow.add_edge("process_query", "generate_response")
        workflow.add_edge("generate_response", "check_hitl")
        
        # Conditional edge based on HITL requirement
        workflow.add_conditional_edges(
            "check_hitl",
            self.route_hitl,
            {
                "save": "save_interaction",
                "escalate": END
            }
        )
        
        workflow.add_edge("save_interaction", "trim_state")
        workflow.add_edge("trim_state", END)
        
        return workflow
    
    def process_query_node(self, state: AgentState) -> AgentState:
        """
        Node to process the incoming query.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state
        """
        # Get the latest message
        if not state['messages']:
            return state
        
        latest_message = state['messages'][-1]
        
        # Extract query
        if hasattr(latest_message, 'type') and latest_message.type == 'human':
            query = latest_message.content
            state['metadata']['current_query'] = query
        
        return state
    
    def fetch_history_node(self, state: AgentState) -> AgentState:
        """
        Node to fetch user history from long-term memory.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with user history
        """
        user_id = state.get('user_id', '')
        
        if user_id:
            # Load user history
            history_data = self.memory_manager.load_long_term_memory(user_id)
            state['user_history'] = history_data.get('user_history', [])
            
            # Update metadata
            state['metadata']['history_loaded'] = True
            state['metadata']['history_count'] = len(state['user_history'])
        
        return state
    
    def generate_response_node(self, state: AgentState) -> AgentState:
        """
        Node to generate response using query processor.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with response
        """
        query = state['metadata'].get('current_query', '')
        
        if not query:
            return state
        
        # Generate response
        result = self.query_processor.generate_response(
            query,
            state.get('user_history', [])
        )
        
        # Add response to messages
        response_message = AIMessage(
            content=result['response'],
            additional_kwargs={
                'category': result.get('category'),
                'confidence': result.get('confidence'),
                'timestamp': self.response_formatter.format_with_timestamp("")
            }
        )
        
        state['messages'].append(response_message)
        state['requires_hitl'] = result.get('requires_hitl', False)
        state['metadata']['response_category'] = result.get('category')
        
        return state
    
    def check_hitl_node(self, state: AgentState) -> AgentState:
        """
        Node to check if human intervention is required.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state
        """
        # The requires_hitl flag is already set in generate_response_node
        if state.get('requires_hitl', False):
            state['metadata']['hitl_requested'] = True
            state['metadata']['hitl_reason'] = 'Complex query requiring human review'
        
        return state
    
    def save_interaction_node(self, state: AgentState) -> AgentState:
        """
        Node to save the interaction to long-term memory.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state
        """
        user_id = state.get('user_id', '')
        query = state['metadata'].get('current_query', '')
        
        if not user_id or not query:
            return state
        
        # Get the response
        response = ''
        for msg in reversed(state['messages']):
            if hasattr(msg, 'type') and msg.type == 'ai':
                response = getattr(msg, 'content', '')
                break
        
        # Save to long-term memory
        metadata = {
            'category': state['metadata'].get('response_category'),
            'thread_id': state.get('thread_id', '')
        }
        
        self.memory_manager.append_to_history(
            user_id,
            query,
            response,
            metadata
        )
        
        # Update state
        state = add_user_history_entry(state, query, response, metadata)
        
        return state
    
    def trim_state_node(self, state: AgentState) -> AgentState:
        """
        Node to trim messages and manage context window.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with trimmed messages
        """
        # Trim messages to last 5
        state = trim_messages(state, max_messages=5)
        
        # Filter out very short or irrelevant messages
        state = filter_messages(state)
        
        return state
    
    def route_hitl(self, state: AgentState) -> str:
        """
        Route based on HITL requirement.
        
        Args:
            state: Current agent state
            
        Returns:
            Next node name
        """
        if state.get('requires_hitl', False):
            return "escalate"
        return "save"
    
    def compile_graph(self) -> Any:
        """
        Compile the graph with checkpointer.
        
        Returns:
            Compiled graph ready for execution
        """
        workflow = self.build_graph()
        checkpointer = self.memory_manager.get_checkpointer()
        
        return workflow.compile(checkpointer=checkpointer)