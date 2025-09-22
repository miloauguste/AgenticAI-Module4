"""
Query Processing Module
Handles customer query processing and response generation.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import re


class MockLLMNode:
    """Mock LLM node with predefined responses for authentication queries."""
    
    def __init__(self):
        """Initialize with mock responses for authentication queries."""
        self.mock_responses = {
            "how do i reset my password": """To reset your password:

1. Visit our login page and click "Forgot Password?"
2. Enter your registered email address
3. Check your email for a password reset link (may take up to 5 minutes)
4. Click the link and create a new secure password
5. Your new password must contain at least 8 characters with uppercase, lowercase, and numbers

If you don't receive the email, check your spam folder or contact support for assistance.""",

            "i forgot my password can you help": """I can definitely help you recover your password! Here's what to do:

1. Go to the login page and select "Forgot Password?"
2. Enter the email address associated with your account
3. You'll receive a password reset email within 5 minutes
4. Follow the secure link in the email to create a new password
5. Make sure your new password is strong and unique

If you're having trouble receiving the email, please check your spam folder first.""",

            "my account is locked what should i do": """If your account is locked, here are the steps to unlock it:

1. Wait 15 minutes - temporary locks often resolve automatically
2. Try the "Forgot Password?" option to reset your credentials
3. Clear your browser cache and cookies, then try logging in again
4. If still locked, it may be due to multiple failed login attempts

For immediate assistance, contact our support team at support@company.com with your username or email address.""",

            "how do i change my password": """To change your password while logged in:

1. Go to Account Settings → Security
2. Click on "Change Password"
3. Enter your current password
4. Create a new secure password (8+ characters, mixed case, numbers)
5. Confirm the new password
6. Click "Update Password"

You'll receive a confirmation email once the change is successful. For security, you'll be logged out of all devices.""",

            "i can't log in to my account": """Let's troubleshoot your login issue:

1. **Check your credentials**: Ensure you're using the correct email/username and password
2. **Try password reset**: Use "Forgot Password?" if you're unsure about your password
3. **Clear browser data**: Clear cache, cookies, and try a different browser
4. **Check account status**: Your account might be temporarily locked
5. **Verify email**: Make sure you've verified your email address

If none of these work, please contact support with your username or registered email.""",

            "why am i getting invalid credentials error": """The "invalid credentials" error usually means:

1. **Incorrect password**: Try using "Forgot Password?" to reset it
2. **Wrong email/username**: Double-check you're using the right login credentials
3. **Account not verified**: Check if you need to verify your email address
4. **Caps Lock**: Ensure Caps Lock isn't affecting your password
5. **Browser issues**: Clear cache/cookies or try a different browser

If you're certain your credentials are correct, your account may be locked. Contact support for assistance.""",

            "how do i enable two-factor authentication": """To enable two-factor authentication (2FA):

1. Go to Account Settings → Security
2. Find "Two-Factor Authentication" section
3. Click "Enable 2FA"
4. Download an authenticator app (Google Authenticator, Authy, etc.)
5. Scan the QR code with your authenticator app
6. Enter the 6-digit code from your app to verify
7. Save your backup codes in a secure location

2FA adds an extra layer of security to protect your account from unauthorized access.""",

            "i lost my 2fa device how do i access my account": """If you lost your 2FA device, here's how to regain access:

1. **Use backup codes**: If you saved backup codes during 2FA setup, use one of those
2. **Account recovery**: Contact our support team with verification details:
   - Your full name and email address
   - Last known password
   - Recent account activity details
3. **Alternative verification**: We may ask for additional identity verification
4. **Device replacement**: Once verified, we'll help you set up 2FA on a new device

For security reasons, this process may take 24-48 hours to complete.""",

            "can i use my email instead of username to login": """Yes! You can log in using either:

1. **Email address**: Enter your full email address in the username field
2. **Username**: Use your chosen username if you prefer

Both methods work with the same password. If you're having trouble:
- Make sure you're using the correct email format (user@domain.com)
- Try both your email and username to see which one works
- Use "Forgot Password?" if you're unsure about your password

The system accepts both login methods for your convenience.""",

            "my session keeps timing out why": """Session timeouts can occur for several reasons:

1. **Inactivity**: Sessions automatically expire after 30 minutes of inactivity for security
2. **Browser settings**: Check if your browser is set to clear cookies/data
3. **Network issues**: Unstable connections can cause session interruptions
4. **Multiple devices**: Logging in from another device may end your current session
5. **Security settings**: Enhanced security settings may reduce session duration

To minimize timeouts:
- Stay active in your account
- Check "Remember me" if available
- Ensure stable internet connection
- Contact support if timeouts are unusually frequent"""
        }
    
    def get_response(self, query: str) -> str:
        """Get mock LLM response for authentication queries."""
        query_lower = query.lower().strip()
        
        # Direct match first
        if query_lower in self.mock_responses:
            return self.mock_responses[query_lower]
        
        # Fuzzy matching for similar queries
        for key in self.mock_responses:
            if self._is_similar_query(query_lower, key):
                return self.mock_responses[key]
        
        # Default response for unmatched queries
        return """I understand you're having an account or authentication issue. Here are some general steps that might help:

1. Try resetting your password using "Forgot Password?"
2. Clear your browser cache and cookies
3. Check your email for any account notifications
4. Contact our support team if the issue persists

Is there a specific authentication problem you're experiencing?"""
    
    def _is_similar_query(self, query: str, reference: str) -> bool:
        """Check if queries are similar using keyword matching."""
        query_words = set(query.split())
        reference_words = set(reference.split())
        
        # Calculate overlap
        overlap = len(query_words & reference_words)
        min_length = min(len(query_words), len(reference_words))
        
        # Consider similar if >50% overlap or contains key phrases
        similarity_ratio = overlap / min_length if min_length > 0 else 0
        
        return similarity_ratio > 0.5


class QueryProcessor:
    """Processes customer support queries and generates responses."""
    
    def __init__(self):
        """Initialize the query processor with knowledge base."""
        self.knowledge_base = self._build_knowledge_base()
        self.mock_llm = MockLLMNode()
        self.complex_indicators = [
            'refund', 'legal', 'escalate', 'manager', 'complaint',
            'lawsuit', 'security breach', 'data leak', 'unauthorized access',
            'fraud', 'billing dispute', 'cancel subscription'
        ]
        
    def _build_knowledge_base(self) -> Dict[str, Dict[str, Any]]:
        """Build the internal knowledge base for common queries."""
        return {
            'password_reset': {
                'keywords': ['password', 'reset', 'forgot', 'login', 'access'],
                'response': """To reset your password:

1. Go to the login page at https://login.techtrendinnovations.com
2. Click on "Forgot Password?" link
3. Enter your registered email address
4. Check your email for the password reset link
5. Click the link and create a new password
6. Your new password must be at least 8 characters with uppercase, lowercase, and numbers

The reset link expires in 24 hours. If you don't receive the email, please check your spam folder.""",
                'category': 'account'
            },
            'billing': {
                'keywords': ['billing', 'payment', 'invoice', 'charge', 'subscription', 'cost'],
                'response': """For billing-related inquiries:

• View billing details: Account Settings > Billing & Payments
• Download invoices: Billing section > Invoice History
• Update payment method: Settings > Payment Methods
• View subscription plans: Account > Subscription

If you notice any incorrect charges, please provide the transaction ID and date for immediate assistance.""",
                'category': 'billing'
            },
            'features': {
                'keywords': ['feature', 'how to', 'tutorial', 'guide', 'use'],
                'response': """I can help you with our features! Here are some quick guides:

• Getting Started Guide: https://docs.techtrendinnovations.com/getting-started
• Feature Tutorials: https://docs.techtrendinnovations.com/features
• Video Walkthroughs: https://learn.techtrendinnovations.com
• API Documentation: https://api.techtrendinnovations.com/docs

Which specific feature would you like to learn about?""",
                'category': 'support'
            },
            'account': {
                'keywords': ['account', 'profile', 'settings', 'preferences'],
                'response': """For account management:

• Edit Profile: Settings > Profile Information
• Security Settings: Settings > Security & Privacy
• Notification Preferences: Settings > Notifications
• Data Export: Settings > Privacy > Export Data
• Account Deletion: Settings > Privacy > Delete Account

What specific account setting would you like to modify?""",
                'category': 'account'
            },
            'technical_issue': {
                'keywords': ['error', 'bug', 'not working', 'crash', 'issue', 'problem'],
                'response': """I'll help you resolve this technical issue. Please provide:

1. Error message (if any)
2. What you were trying to do
3. Browser/device information
4. When the issue started

In the meantime, try these quick fixes:
• Clear browser cache and cookies
• Try a different browser
• Disable browser extensions
• Check your internet connection""",
                'category': 'technical'
            }
        }
    
    def analyze_query(self, query: str) -> Tuple[str, float]:
        """
        Analyze query and determine the best matching category.
        
        Args:
            query: User's query
            
        Returns:
            Tuple of (category, confidence_score)
        """
        query_lower = query.lower()
        best_match = ('general', 0.0)
        
        for category, data in self.knowledge_base.items():
            score = sum(
                1 for keyword in data['keywords']
                if keyword in query_lower
            )
            
            if score > best_match[1]:
                best_match = (category, score)
        
        # Normalize confidence score
        if best_match[1] > 0:
            confidence = min(best_match[1] / 3.0, 1.0)
            return best_match[0], confidence
        
        return 'general', 0.0
    
    def is_complex_query(self, query: str) -> bool:
        """
        Determine if query requires human intervention.
        
        Args:
            query: User's query
            
        Returns:
            bool: True if complex, False otherwise
        """
        query_lower = query.lower()
        
        # Check for complex indicators
        if any(indicator in query_lower for indicator in self.complex_indicators):
            return True
        
        # Check for multiple question marks (frustration)
        if query.count('?') > 2:
            return True
        
        # Check for ALL CAPS (anger)
        if query.isupper() and len(query) > 20:
            return True
        
        return False
    
    def _is_authentication_query(self, query: str) -> bool:
        """
        Determine if query is related to authentication/account access.
        
        Args:
            query: User's query
            
        Returns:
            bool: True if authentication-related, False otherwise
        """
        auth_keywords = [
            'password', 'login', 'log in', 'sign in', 'access', 'account',
            'credentials', 'locked', 'reset', 'forgot', 'change',
            '2fa', 'two-factor', 'authentication', 'authenticator',
            'session', 'timeout', 'email', 'username', 'invalid'
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in auth_keywords)
    
    def generate_response(
        self,
        query: str,
        user_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate response for a query.
        
        Args:
            query: User's query
            user_history: User's interaction history
            
        Returns:
            Dict containing response and metadata
        """
        category, confidence = self.analyze_query(query)
        
        # Check if complex query
        if self.is_complex_query(query):
            return {
                'response': "I understand this is an important matter that requires specialized attention. I'm escalating your query to our human support team who will review it and respond within 2 business hours. You'll receive a notification once they've reviewed your case.",
                'requires_hitl': True,
                'category': 'escalation',
                'confidence': 1.0
            }
        
        # Check if this is an authentication query and use MockLLM
        if self._is_authentication_query(query):
            response_text = self.mock_llm.get_response(query)
            return {
                'response': response_text,
                'requires_hitl': False,
                'category': 'authentication',
                'confidence': 0.95,
                'source': 'mock_llm'
            }
        
        # Generate personalized response based on history
        response_text = self._generate_personalized_response(
            query, category, confidence, user_history
        )
        
        return {
            'response': response_text,
            'requires_hitl': False,
            'category': category,
            'confidence': confidence
        }
    
    def _generate_personalized_response(
        self,
        query: str,
        category: str,
        confidence: float,
        user_history: List[Dict[str, Any]]
    ) -> str:
        """Generate personalized response based on user history."""
        
        base_response = ""
        
        # Get base response from knowledge base
        if category in self.knowledge_base and confidence > 0.3:
            base_response = self.knowledge_base[category]['response']
        else:
            base_response = f"""Thank you for your question about "{query}". 

I'd be happy to help you with this. Could you please provide more details about:
• What you're trying to accomplish
• Any error messages you're seeing
• When this issue started

This will help me provide you with the most accurate assistance."""
        
        # Add personalization based on history
        if user_history:
            recent_queries = [h.get('query', '') for h in user_history[-3:]]
            
            # Check for related previous queries
            for prev_query in recent_queries:
                if self._are_queries_related(query, prev_query):
                    base_response = f"I see you previously asked about similar topics. {base_response}\n\nBased on your history, I can also help with any follow-up questions."
                    break
        
        return base_response
    
    def _are_queries_related(self, query1: str, query2: str) -> bool:
        """Check if two queries are related."""
        # Simple word overlap check
        words1 = set(re.findall(r'\w+', query1.lower()))
        words2 = set(re.findall(r'\w+', query2.lower()))
        
        # Remove common words
        common_words = {'the', 'a', 'an', 'is', 'how', 'what', 'when', 'where', 'can', 'my', 'i'}
        words1 -= common_words
        words2 -= common_words
        
        overlap = len(words1 & words2)
        return overlap >= 2


class ResponseFormatter:
    """Formats responses for better presentation."""
    
    @staticmethod
    def format_with_timestamp(response: str) -> str:
        """Add timestamp to response."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp}]\n\n{response}"
    
    @staticmethod
    def format_with_metadata(
        response: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Add metadata footer to response."""
        footer = "\n\n---\n"
        footer += f"Category: {metadata.get('category', 'general')}\n"
        footer += f"Confidence: {metadata.get('confidence', 0):.0%}"
        
        return response + footer
    
    @staticmethod
    def truncate_long_response(response: str, max_length: int = 500) -> str:
        """Truncate response if too long."""
        if len(response) <= max_length:
            return response
        
        return response[:max_length] + "...\n\n[Response truncated. Would you like more details?]"