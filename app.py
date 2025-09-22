"""
Streamlit UI for Customer Support Agent
"""

import streamlit as st
import os
from datetime import datetime
from main import CustomerSupportAgent

# Page configuration
st.set_page_config(
    page_title="TechTrend Support Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = CustomerSupportAgent()

if 'session_active' not in st.session_state:
    st.session_state.session_active = False

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'user_id' not in st.session_state:
    st.session_state.user_id = ""

if 'thread_id' not in st.session_state:
    st.session_state.thread_id = ""

if 'hitl_queue' not in st.session_state:
    st.session_state.hitl_queue = []

# Helper function for HITL proposed actions
def get_proposed_action_text(query):
    """Generate user-friendly text describing the AI's proposed action based on the query."""
    query_lower = query.lower()
    
    if 'password' in query_lower and ('reset' in query_lower or 'forgot' in query_lower):
        return "Send password reset link to user's registered email address"
    elif 'account' in query_lower and 'locked' in query_lower:
        return "Unlock user account and send confirmation email"
    elif 'refund' in query_lower or 'billing' in query_lower:
        return "Process refund request and update billing records"
    elif '2fa' in query_lower or 'two-factor' in query_lower:
        return "Provide 2FA setup instructions and backup codes"
    elif 'delete' in query_lower and 'account' in query_lower:
        return "Initiate account deletion process (30-day grace period)"
    elif 'subscription' in query_lower and 'cancel' in query_lower:
        return "Cancel subscription and provide confirmation"
    elif 'security' in query_lower or 'breach' in query_lower:
        return "Escalate to security team for immediate investigation"
    elif 'legal' in query_lower or 'lawsuit' in query_lower:
        return "Forward to legal department for review"
    else:
        return "Provide comprehensive support response with escalation option"

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A8A;
        text-align: center;
        padding: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #64748B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .user-message {
        background-color: #3B82F6;
        color: white;
        padding: 1rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        margin-left: 20%;
    }
    .assistant-message {
        background-color: #F1F5F9;
        color: #1E293B;
        padding: 1rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        margin-right: 20%;
    }
    .hitl-message {
        background-color: #FEF3C7;
        border: 2px solid #F59E0B;
        color: #92400E;
        padding: 1rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
    }
    .hitl-card {
        background-color: #FEF9E7;
        border: 2px solid #F59E0B;
        border-radius: 1rem;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .approval-button {
        background-color: #10B981;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        cursor: pointer;
        margin: 0.25rem;
    }
    .reject-button {
        background-color: #EF4444;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        cursor: pointer;
        margin: 0.25rem;
    }
    .proposed-action {
        background-color: #EFF6FF;
        border-left: 4px solid #3B82F6;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
    }
    .session-info {
        background-color: #EFF6FF;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3B82F6;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">TechTrend Innovations</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Customer Support Agent</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("Session Management")
    
    if not st.session_state.session_active:
        st.subheader("Initialize Session")
        
        user_id_input = st.text_input(
            "User ID",
            placeholder="e.g., user_12345",
            key="user_id_input"
        )
        
        thread_id_input = st.text_input(
            "Thread ID",
            placeholder="e.g., thread_001",
            key="thread_id_input"
        )
        
        if st.button("Start Session", type="primary", use_container_width=True):
            if user_id_input and thread_id_input:
                try:
                    session_info = st.session_state.agent.start_session(
                        user_id_input,
                        thread_id_input
                    )
                    
                    st.session_state.user_id = user_id_input
                    st.session_state.thread_id = thread_id_input
                    st.session_state.session_active = True
                    
                    # Add welcome message
                    welcome_msg = {
                        'role': 'assistant',
                        'content': f"Welcome back! I've loaded {session_info['history_count']} previous interactions. How can I help you today?",
                        'timestamp': datetime.now().isoformat()
                    }
                    st.session_state.messages.append(welcome_msg)
                    
                    st.success(f"Session started: {session_info['session_id']}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error starting session: {str(e)}")
            else:
                st.warning("Please enter both User ID and Thread ID")
    
    else:
        st.markdown(f"""
        <div class="session-info">
            <strong>Active Session</strong><br>
            User: {st.session_state.user_id}<br>
            Thread: {st.session_state.thread_id}
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # User History
        st.subheader("📜 User History")
        
        if st.button("Load History", use_container_width=True):
            try:
                history = st.session_state.agent.get_user_history(
                    st.session_state.user_id,
                    limit=5
                )
                
                if history:
                    for idx, entry in enumerate(history, 1):
                        with st.expander(f"{idx}. {entry['query'][:50]}..."):
                            st.write(f"**Query:** {entry['query']}")
                            st.write(f"**Resolution:** {entry['resolution'][:200]}...")
                            st.caption(f"Time: {entry['timestamp']}")
                else:
                    st.info("No history available")
            except Exception as e:
                st.error(f"Error loading history: {str(e)}")
        
        st.divider()
        
        # HITL Queue
        pending_count = sum(1 for item in st.session_state.hitl_queue if item.get('status') == 'pending')
        if pending_count > 0:
            st.subheader(f"🚨 Human Review Queue ({pending_count})")
            st.error(f"⚠️ **{pending_count} urgent review(s) required** - Customer waiting for response")
        else:
            st.subheader("🚨 Human Review Queue")
        st.caption("Review and approve AI responses for complex or sensitive customer queries")
        
        # Add guidance for HITL reviews
        with st.expander("ℹ️ Review Guidelines", expanded=False):
            st.markdown("""
            **When to Approve:**
            - ✅ AI response is accurate and helpful
            - ✅ Proposed action is safe and appropriate
            - ✅ Customer's issue can be resolved as suggested
            
            **When to Escalate:**
            - ❌ Security concerns or potential fraud
            - ❌ Legal implications or compliance issues
            - ❌ Complex technical problems requiring specialist
            - ❌ Customer expressing strong dissatisfaction
            
            **Remember:**
            - Customer is waiting for your decision
            - Add personalized feedback when possible
            - Document escalation reasons clearly
            """)
        
        if st.session_state.hitl_queue:
            
            for idx, item in enumerate(st.session_state.hitl_queue):
                if item.get('status') == 'pending':
                    with st.container():
                        st.markdown(f"""
                        <div class="hitl-card">
                            <h4>🔍 Review Required</h4>
                            <p><strong>Customer Query:</strong><br>"{item['query']}"</p>
                            <div class="proposed-action">
                                <strong>🤖 AI Proposed Action:</strong><br>
                                {get_proposed_action_text(item['query'])}
                            </div>
                            <p><strong>⏰ Received:</strong> {item['timestamp'][:19]}</p>
                            <p><em>This query requires human approval due to complexity or sensitivity.</em></p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown("**👤 Human Decision Required:**")
                        col1, col2, col3 = st.columns([2, 2, 1])
                        
                        # Add feedback inputs before action buttons
                        st.markdown("**💬 Add feedback for customer (optional):**")
                        feedback_col1, feedback_col2 = st.columns(2)
                        
                        with feedback_col1:
                            approve_feedback = st.text_area(
                                "Approval message:", 
                                key=f"approve_feedback_{idx}", 
                                placeholder="e.g., 'Resolution approved by support team. You should receive the password reset link within 5 minutes.'",
                                height=60
                            )
                        
                        with feedback_col2:
                            reject_feedback = st.text_area(
                                "Escalation reason:", 
                                key=f"reject_feedback_{idx}", 
                                placeholder="e.g., 'This requires specialized security team review due to account compromise indicators.'",
                                height=60
                            )
                        
                        with col1:
                            if st.button("✅ Approve Resolution", key=f"approve_{idx}", help="Approve the AI's proposed action", type="primary"):
                                result = st.session_state.agent.approve_hitl(
                                    st.session_state.user_id,
                                    st.session_state.thread_id,
                                    True,
                                    approve_feedback or "Resolution approved by human agent"
                                )
                                item['status'] = 'approved'
                                st.session_state.messages.append({
                                    'role': 'assistant',
                                    'content': result['message'],
                                    'timestamp': datetime.now().isoformat()
                                })
                                st.success("✅ Resolution approved!")
                                st.rerun()
                        
                        with col2:
                            if st.button("❌ Reject & Escalate", key=f"reject_{idx}", help="Reject and escalate to specialized team"):
                                result = st.session_state.agent.approve_hitl(
                                    st.session_state.user_id,
                                    st.session_state.thread_id,
                                    False,
                                    reject_feedback or "Escalated to specialized support team for further review"
                                )
                                item['status'] = 'rejected'
                                st.session_state.messages.append({
                                    'role': 'assistant',
                                    'content': result['message'],
                                    'timestamp': datetime.now().isoformat()
                                })
                                st.warning("⚠️ Request escalated to specialized team")
                                st.rerun()
                        
                        with col3:
                            if st.button("⏸️ Defer", key=f"defer_{idx}", help="Mark for later review"):
                                st.info("📌 Marked for later review")
                        
                        st.divider()
        else:
            st.success("✅ All clear! No items requiring human review.")
        
        st.divider()
        
        # Session Controls
        if st.button("🔄 Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        if st.button("🚪 End Session", type="secondary", use_container_width=True):
            st.session_state.session_active = False
            st.session_state.messages = []
            st.session_state.hitl_queue = []
            st.rerun()

# Main chat area
if st.session_state.session_active:
    # Display chat messages
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            role = message.get('role')
            content = message.get('content')
            timestamp = message.get('timestamp', '')
            
            if role == 'user':
                st.markdown(
                    f'<div class="user-message">{content}<br><small>{timestamp[:19] if timestamp else ""}</small></div>',
                    unsafe_allow_html=True
                )
            elif role == 'assistant':
                if message.get('requires_hitl'):
                    st.markdown(
                        f'''<div class="hitl-message">
                        <strong>🚨 Human Review Required</strong><br>
                        {content}<br>
                        <em>This response is pending human approval in the review queue →</em><br>
                        <small>{timestamp[:19] if timestamp else ""}</small>
                        </div>''',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'<div class="assistant-message">🤖 {content}<br><small>{timestamp[:19] if timestamp else ""}</small></div>',
                        unsafe_allow_html=True
                    )
    
    # Chat input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Add user message
        user_msg = {
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now().isoformat()
        }
        st.session_state.messages.append(user_msg)
        
        # Process message
        with st.spinner("Processing..."):
            try:
                result = st.session_state.agent.process_message(
                    st.session_state.user_id,
                    st.session_state.thread_id,
                    user_input
                )
                
                # Add assistant response
                assistant_msg = {
                    'role': 'assistant',
                    'content': result['response'],
                    'timestamp': datetime.now().isoformat(),
                    'requires_hitl': result.get('requires_hitl', False)
                }
                st.session_state.messages.append(assistant_msg)
                
                # Add to HITL queue if needed
                if result.get('requires_hitl'):
                    st.session_state.hitl_queue.append({
                        'query': user_input,
                        'user_id': st.session_state.user_id,
                        'thread_id': st.session_state.thread_id,
                        'timestamp': datetime.now().isoformat(),
                        'status': 'pending'
                    })
                
                st.rerun()
            except Exception as e:
                st.error(f"Error processing message: {str(e)}")

else:
    # Show welcome screen when no session
    st.info("👈 Please initialize a session from the sidebar to begin")
    
    # Display features
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🎯 Features")
        st.markdown("""
        - Intelligent query processing
        - Context-aware responses
        - Memory persistence
        """)
    
    with col2:
        st.markdown("### 🔄 Memory Management")
        st.markdown("""
        - Short-term session memory
        - Long-term user history
        - Automatic context trimming
        """)
    
    with col3:
        st.markdown("### 👥 Human-in-Loop")
        st.markdown("""
        - Complex query escalation
        - Human review workflow
        - Approval management
        """)

# Footer
st.divider()
st.caption("Edureka Assignment - Module 4 Assignment  Building AI Agents with LangGraph")
st.caption("Developed by: Milo Auguste Jr")