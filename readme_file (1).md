# Customer Support Agent with LangGraph

A production-ready AI-powered customer support agent built with LangGraph, featuring memory management, human-in-the-loop workflows, and state persistence.

## 🏗️ Architecture

### Core Components

```
customer-support-agent/
├── agent_state.py          # State schema and management
├── memory_manager.py       # Memory persistence layer
├── query_processor.py      # Query analysis and response generation
├── graph_builder.py        # LangGraph agent construction
├── main.py                 # Main application entry point
├── app.py                  # Streamlit UI
├── requirements.txt        # Project dependencies
├── .env.template          # Environment variables template
└── README.md              # This file
```

### State Management

The agent uses a sophisticated state schema with:
- **Short-term memory**: Current session messages
- **Long-term memory**: Persistent user interaction history
- **Metadata tracking**: User ID, thread ID, and session information
- **HITL flags**: Human intervention requirements

## 🚀 Installation & Setup

### Step 1: Create Virtual Environment

Navigate to your project directory (module4):

```bash
cd D:\module4
```

Create and activate virtual environment:

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment

1. Copy the environment template:
```bash
cp .env.template .env
```

2. Edit `.env` file with your configuration:
```
OPENAI_API_KEY=your_api_key_here
STORAGE_PATH=./memory_storage
```

## 💻 Usage

### Command Line Interface

Run the CLI application:

```bash
python main.py
```

Follow the prompts to:
1. Enter User ID
2. Enter Thread ID
3. Start chatting with the agent

**CLI Commands:**
- `quit` - Exit the application
- `history` - View conversation history
- `clear` - Clear conversation history

### Web Interface (Streamlit)

Launch the web UI:

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 📋 Features

### 1. Memory Schema Implementation

The agent maintains two types of memory:

**AgentState Structure:**
```python
{
    'messages': List[Dict],           # Current session messages
    'user_history': List[Dict],       # Historical interactions
    'user_id': str,                   # User identifier
    'thread_id': str,                 # Thread identifier
    'metadata': Dict,                 # Additional metadata
    'requires_hitl': bool,            # HITL flag
    'hitl_approved': Optional[bool]   # HITL approval status
}
```

### 2. State Management

- **StateGraph**: Manages agent state transitions
- **State Reducer**: Handles message updates with `add_messages`
- **Message Trimming**: Keeps last 5 messages for context management
- **Message Filtering**: Removes irrelevant content

### 3. Memory Persistence

**Short-term Memory:**
- Uses `MemorySaver` for session persistence
- Maintains conversation context within sessions

**Long-term Memory:**
- JSON file-based storage by default
- Extensible to external databases
- Tracks user interaction history across sessions

### 4. Query Processing

The agent handles:
- Password reset queries
- Billing inquiries
- Feature questions
- Account management
- Technical issues

**Complex Query Detection:**
- Identifies queries requiring human intervention
- Escalates based on keywords and sentiment
- Maintains escalation queue

### 5. Human-in-the-Loop (HITL)

**Workflow:**
1. Agent detects complex query
2. Query added to review queue
3. Human agent reviews
4. Approval/rejection with feedback
5. User notification

### 6. State Validation

Ensures data consistency:
- Validates user_id and thread_id
- Checks message structure
- Verifies metadata integrity

## 🔧 Configuration

### Memory Storage

Default storage location: `./memory_storage`

User data is stored in JSON format:
```json
{
  "user_id": "user_12345",
  "user_history": [
    {
      "query": "How to reset password?",
      "resolution": "Password reset link sent",
      "timestamp": "2025-01-15T10:30:00",
      "metadata": {}
    }
  ],
  "metadata": {},
  "last_updated": "2025-01-15T10:30:00"
}
```

### External Memory Integration

To integrate with external databases, extend the `ExternalMemoryStore` class in `memory_manager.py`:

```python
class PostgreSQLMemoryStore(ExternalMemoryStore):
    def __init__(self, connection_string):
        self.conn = psycopg2.connect(connection_string)
        # Implementation details
```

## 📊 Knowledge Base

The agent includes pre-configured responses for:

1. **Password Reset**
   - Step-by-step instructions
   - Security guidelines

2. **Billing**
   - Invoice access
   - Payment methods
   - Subscription management

3. **Features**
   - Documentation links
   - Tutorial resources

4. **Account Management**
   - Profile settings
   - Security configuration

5. **Technical Support**
   - Error troubleshooting
   - System diagnostics

## 🎯 Advanced Features

### Multiple Schemas

Separate schemas for different data types:
```python
# User profile schema
class UserProfileState(TypedDict):
    user_id: str
    name: str
    email: str
    preferences: Dict

# Query history schema
class QueryHistoryState(TypedDict):
    user_id: str
    queries: List[Dict]
    resolution_rate: float
```

### External Memory Integration

Configure database connection in `.env`:
```
DATABASE_URL=postgresql://user:password@localhost/supportdb
```

Implement database-backed memory:
```python
from memory_manager import ExternalMemoryStore

external_store = ExternalMemoryStore(
    connection_string=os.getenv('DATABASE_URL')
)
```

### Enhanced HITL Workflow

The UI provides:
- Real-time escalation queue
- One-click approval/rejection
- Feedback collection
- Status tracking

## 🧪 Testing

Test the agent with various queries:

**Simple Queries:**
- "How do I reset my password?"
- "Where can I find my billing information?"
- "How to use the analytics feature?"

**Complex Queries (HITL Triggered):**
- "I need a refund for my subscription"
- "There's a security breach in my account"
- "I want to speak with your manager"

## 📈 Deployment

### Local Deployment

1. Ensure virtual environment is activated
2. Run the application:
```bash
# CLI version
python main.py

# Web UI version
streamlit run app.py
```

### Community Cloud Deployment

1. Create a GitHub repository with your code
2. Push to GitHub:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-repo-url>
git push -u origin main
```

3. Deploy on Streamlit Community Cloud:
   - Visit share.streamlit.io
   - Connect GitHub repository
   - Configure environment variables in secrets
   - Deploy

### Environment Variables for Deployment

Add to Streamlit secrets:
```toml
OPENAI_API_KEY = "your_api_key"
STORAGE_PATH = "./memory_storage"
```

## 🔒 Security

- API keys stored in environment variables
- No hardcoded credentials
- User data isolated by user_id
- Secure state validation

## 🐛 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**2. Memory Storage Errors**
```bash
# Create storage directory manually
mkdir memory_storage
```

**3. Module Not Found**
```bash
# Ensure virtual environment is activated
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

**4. Streamlit Port Conflict**
```bash
# Run on different port
streamlit run app.py --server.port 8502
```

## 📚 API Reference

### CustomerSupportAgent

Main agent class for customer support operations.

**Methods:**

```python
start_session(user_id: str, thread_id: str) -> Dict[str, Any]
"""Initialize a support session"""

process_message(user_id: str, thread_id: str, message: str) -> Dict[str, Any]
"""Process user message and generate response"""

get_user_history(user_id: str, limit: int = 10) -> List[Dict]
"""Retrieve user interaction history"""

approve_hitl(user_id: str, thread_id: str, approved: bool, feedback: str) -> Dict
"""Approve or reject HITL escalation"""
```

### MemoryManager

Handles memory persistence and retrieval.

**Methods:**

```python
save_long_term_memory(user_id: str, user_history: List, metadata: Dict) -> bool
"""Save user history to persistent storage"""

load_long_term_memory(user_id: str) -> Dict
"""Load user history from storage"""

append_to_history(user_id: str, query: str, resolution: str, metadata: Dict) -> bool
"""Add new interaction to history"""

get_recent_history(user_id: str, limit: int) -> List
"""Get recent history entries"""
```

## 🤝 Contributing

This is an academic project. For suggestions:
1. Review the code structure
2. Identify improvements
3. Document changes
4. Test thoroughly

## 📝 License

This project is created for educational purposes as part of the Building AI Agents with LangGraph course.

## 🎓 Course Information

**Module:** Module 4 - Building AI Agents with LangGraph
**Institution:** Edureka / Veranda Enterprise
**Assignment:** Customer Support Agent Implementation

## 💡 Tips for Success

1. **Start with CLI**: Test basic functionality before using UI
2. **Check Logs**: Monitor console output for debugging
3. **Use Valid IDs**: Ensure user_id and thread_id follow format
4. **Test HITL**: Try queries that trigger escalation
5. **Clear Storage**: Remove old data if testing fresh

## 🔄 Version Control

Recommended `.gitignore`:
```
venv/
__pycache__/
*.pyc
.env
memory_storage/
*.log
.streamlit/
```

## 📞 Support

For issues related to:
- **LangGraph**: Check documentation at https://langchain-ai.github.io/langgraph/
- **Streamlit**: Visit https://docs.streamlit.io
- **Course**: Contact course instructors

---

**Built with ❤️ using LangGraph and Streamlit**