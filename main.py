import os
import json
from datetime import datetime
from dotenv import load_dotenv

print("Step 1: Loading environment...")
# Load env
load_dotenv(dotenv_path=".env")

print("Step 2: Checking API key...")
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("ERROR: GOOGLE_API_KEY not found in .env file!")
    exit(1)
print(f"[OK] API KEY found (length: {len(api_key)})")

print("Step 3: Importing LangChain...")
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    print("[OK] LangChain imported successfully")
except Exception as e:
    print(f"ERROR importing LangChain: {e}")
    exit(1)

print("Step 4: Initializing LLM...")
try:
    # Using gemini-flash-latest for better compatibility
    llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0, timeout=30)
    print("[OK] LLM initialized successfully (model: gemini-flash-latest, timeout: 30s)")
except Exception as e:
    print(f"ERROR initializing LLM: {e}")
    exit(1)

print("Step 5: Loading knowledge base...")

# Load knowledge base
try:
    with open("knowledge.json", "r") as f:
        knowledge_data = json.load(f)
        if isinstance(knowledge_data, list):
            knowledge_text = "\n".join([str(item) for item in knowledge_data])
        else:
            knowledge_text = json.dumps(knowledge_data, indent=2)
    print(f"[OK] Knowledge base loaded ({len(knowledge_text)} characters)")
except FileNotFoundError:
    print("⚠ knowledge.json not found - using empty knowledge base")
    knowledge_text = ""
except Exception as e:
    print(f"⚠ Error loading knowledge.json: {e} - using empty knowledge base")
    knowledge_text = ""

# ============================================
# FEATURE 4: CONVERSATION MEMORY
# ============================================
class ConversationMemory:
    """Stores conversation history for context"""
    
    def __init__(self, max_history=10):
        self.max_history = max_history
        self.history = []
    
    def add(self, role, message):
        """Add a message to memory"""
        self.history.append({
            "role": role,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        # Keep only last max_history messages
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def get_context(self):
        """Get formatted conversation context"""
        if not self.history:
            return ""
        
        context = "Conversation history:\n"
        for item in self.history:
            role_emoji = "👤" if item["role"] == "user" else "🤖"
            context += f"{role_emoji} {item['role']}: {item['message']}\n"
        return context
    
    def clear(self):
        """Clear all memory"""
        self.history = []
    
    def get_last_user_message(self):
        """Get the last user message"""
        for item in reversed(self.history):
            if item["role"] == "user":
                return item["message"]
        return None

# Initialize conversation memory
conversation_memory = ConversationMemory(max_history=10)

# ============================================
# FEATURE 2: TOOL EXECUTION SYSTEM
# ============================================
class ToolExecutor:
    """Execute various tools/actions"""
    
    def __init__(self):
        self.tools = {
            "capture_lead": self.tool_capture_lead,
            "book_demo": self.tool_book_demo,
            "check_pricing": self.tool_check_pricing,
            "get_support": self.tool_get_support,
            "send_email": self.tool_send_email,
        }
    
    def tool_capture_lead(self, params):
        """Capture lead information"""
        name = params.get("name", "Unknown")
        email = params.get("email", "Unknown")
        platform = params.get("platform", "Unknown")
        phone = params.get("phone", "Not provided")
        
        print(f"\n🎯 LEAD CAPTURED:")
        print(f"   Name: {name}")
        print(f"   Email: {email}")
        print(f"   Platform: {platform}")
        print(f"   Phone: {phone}")
        print(f"   Time: {datetime.now().isoformat()}\n")
        
        return {
            "success": True,
            "message": f"Lead captured: {name} ({email})",
            "data": params
        }
    
    def tool_book_demo(self, params):
        """Book a demo appointment"""
        name = params.get("name", "Unknown")
        email = params.get("email", "Unknown")
        preferred_date = params.get("preferred_date", "Not specified")
        
        print(f"\n📅 DEMO BOOKED:")
        print(f"   Name: {name}")
        print(f"   Email: {email}")
        print(f"   Preferred Date: {preferred_date}")
        print(f"   Time: {datetime.now().isoformat()}\n")
        
        return {
            "success": True,
            "message": f"Demo scheduled for {name} on {preferred_date}",
            "data": params
        }
    
    def tool_check_pricing(self, params):
        """Check pricing information"""
        plan = params.get("plan", "all")
        
        pricing_info = {
            "basic": {"price": "$29/month", "features": ["10 videos", "720p", "Basic support"]},
            "pro": {"price": "$79/month", "features": ["Unlimited videos", "4K", "AI captions", "24/7 support"]},
            "enterprise": {"price": "Custom", "features": ["Custom solutions", "Dedicated support", "API access"]}
        }
        
        if plan == "all":
            return {"success": True, "message": "All plans available", "data": pricing_info}
        return {"success": True, "message": f"Plan: {plan}", "data": pricing_info.get(plan, {})}
    
    def tool_get_support(self, params):
        """Get support information"""
        return {
            "success": True,
            "message": "Support options retrieved",
            "data": {
                "email": "support@autostream.com",
                "phone": "1-800-AUTO-STREAM",
                "hours": "24/7 (Pro plan), 9-5 weekdays (Basic)"
            }
        }
    
    def tool_send_email(self, params):
        """Send email notification"""
        to = params.get("to", "")
        subject = params.get("subject", "")
        body = params.get("body", "")
        
        print(f"\n📧 EMAIL PREPARED:")
        print(f"   To: {to}")
        print(f"   Subject: {subject}")
        print(f"   Body: {body[:50]}...\n")
        
        return {
            "success": True,
            "message": f"Email sent to {to}",
            "data": params
        }
    
    def execute(self, tool_name, params=None):
        """Execute a tool by name"""
        if params is None:
            params = {}
        
        if tool_name in self.tools:
            try:
                return self.tools[tool_name](params)
            except Exception as e:
                return {"success": False, "message": f"Tool error: {str(e)}", "data": {}}
        else:
            return {"success": False, "message": f"Unknown tool: {tool_name}", "data": {}}
    
    def get_available_tools(self):
        """Get list of available tools"""
        return list(self.tools.keys())

# Initialize tool executor
tool_executor = ToolExecutor()

# ============================================
# FEATURE 3: POLICY QUESTION HANDLER
# ============================================
# Policy knowledge base
policy_data = {
    "refund": {
        "question": ["refund", "money back", "cancel", "return"],
        "answer": "Our refund policy: Full refund within 7 days of purchase. After 7 days, refunds are not available but you can cancel your subscription at any time."
    },
    "privacy": {
        "question": ["privacy", "data", "personal", "information"],
        "answer": "Privacy Policy: We collect minimal data needed for service delivery. Your data is encrypted and never sold to third parties. You can request data deletion at any time."
    },
    "terms": {
        "question": ["terms", "conditions", "agreement", "tos"],
        "answer": "Terms of Service: By using AutoStream, you agree to our Terms of Service. Key points: (1) You must be 18+ to use our service, (2) Content you upload remains yours, (3) We can terminate accounts for violations."
    },
    "trial": {
        "question": ["trial", "free", "demo", "test"],
        "answer": "Free Trial: We offer a 7-day free trial on all plans. No credit card required to start. You can upgrade to paid plans anytime during or after the trial."
    },
    "billing": {
        "question": ["billing", "invoice", "payment", "charge"],
        "answer": "Billing: We charge monthly on the same date you signed up. Accepted payment methods: Credit/Debit cards, PayPal. You can update payment info in account settings."
    }
}

def handle_policy_question(user_input):
    """Handle policy-related questions"""
    user_input_lower = user_input.lower()
    
    for policy_key, policy_info in policy_data.items():
        # Check if any keyword matches
        if any(keyword in user_input_lower for keyword in policy_info["question"]):
            return policy_info["answer"]
    
    return None  # Not a policy question

# ============================================
# FEATURE 1: ENHANCED LEAD CAPTURE
# ============================================
# Lead storage
lead_data = {
    "name": None, 
    "email": None, 
    "platform": None,
    "phone": None,
    "company": None,
    "interest": None
}
lead_stage = 0
lead_substage = 0  # For multi-step capture

def mock_lead_capture(name, email, platform, phone=None, company=None, interest=None):
    """Enhanced lead capture with more fields"""
    print(f"\n" + "="*50)
    print(" 🎯 LEAD CAPTURED SUCCESSFULLY!")
    print("="*50)
    print(f" 📛 Name: {name}")
    print(f" 📧 Email: {email}")
    print(f" 📱 Platform: {platform}")
    if phone:
        print(f" 📞 Phone: {phone}")
    if company:
        print(f" 🏢 Company: {company}")
    if interest:
        print(f" 💡 Interest: {interest}")
    print(f" ⏰ Captured at: {datetime.now().isoformat()}")
    print("="*50 + "\n")
    
    # Execute tool
    result = tool_executor.execute("capture_lead", {
        "name": name,
        "email": email,
        "platform": platform,
        "phone": phone,
        "company": company,
        "interest": interest
    })
    
    return result

def demonstrate_lead_capture():
    """Demonstrate lead capture flow"""
    demo_steps = [
        "Step 1: Collect name",
        "Step 2: Collect email", 
        "Step 3: Collect phone (optional)",
        "Step 4: Collect company (optional)",
        "Step 5: Collect platform preference",
        "Step 6: Collect interest area",
        "Step 7: Confirm and store"
    ]
    
    print("\n" + "="*50)
    print(" 📋 LEAD CAPTURE DEMONSTRATION")
    print("="*50)
    for step in demo_steps:
        print(f"  {step}")
    print("="*50 + "\n")

# Simple QA function without embeddings
def query_qa_chain(question):
    try:
        # Get conversation context
        context = conversation_memory.get_context()
        
        prompt = f"""You are a helpful assistant. Use the following knowledge base to answer the question.
    
Knowledge Base:
{knowledge_text}

{context}

Question: {question}

Answer: """
        response = llm.invoke(prompt, timeout=20)  # Timeout for Q&A
        
        # Handle different response formats
        if isinstance(response.content, list):
            # Extract text from list format
            content = ""
            for item in response.content:
                if isinstance(item, dict) and 'text' in item:
                    content += item['text']
                elif isinstance(item, str):
                    content += item
            return content.strip()
        else:
            return response.content.strip()
    except Exception as e:
        error_msg = str(e).lower()
        if "timeout" in error_msg or "deadline" in error_msg:
            return "⏰ Sorry, the request timed out. The timeout is set to 15 seconds. Please try again with a shorter question."
        elif "quota" in error_msg or "resource_exhausted" in error_msg or "429" in error_msg:
            return "📊 Sorry, I've reached my API usage limit. Please try again later or check your Google AI Studio billing."
        else:
            print(f"⚠ API Error in Q&A: {str(e)[:100]}...")
            # Fallback: simple keyword matching
            question_lower = question.lower()
            if "price" in question_lower or "cost" in question_lower:
                return "Based on our knowledge base: Basic plan is $29/month (10 videos, 720p), Pro plan is $79/month (unlimited videos, 4K, AI captions)."
            elif "refund" in question_lower:
                return "According to our policies: No refunds after 7 days."
            elif "support" in question_lower:
                return "Support info: 24/7 support is available only on the Pro plan."
            else:
                return "I apologize, but I'm currently experiencing API issues. Please try again later or contact support."
    print(f"\n Lead captured successfully: {name}, {email}, {platform}\n")

# Intent Detection using LLM
def detect_intent(user_input):
    try:
        # Check for greeting first based on user input
        if any(word in user_input.lower() for word in ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"]):
            return "greeting"

        # Check for policy questions first
        if handle_policy_question(user_input):
            return "policy"

        # Check for tool execution requests
        tool_keywords = {
            "demo": "book_demo",
            "book": "book_demo", 
            "schedule": "book_demo",
            "contact": "capture_lead",
            "call": "capture_lead",
            "support": "get_support",
            "help": "get_support",
            "email": "send_email"
        }
        
        for keyword, tool_name in tool_keywords.items():
            if keyword in user_input.lower():
                return "tool_request"

        # For other intents, use LLM to analyze
        prompt = f"""Analyze the user's message and classify their intent. Choose from:
- pricing: asking about costs, prices, plans, or pricing information
- high_intent: showing interest in buying, purchasing, or getting started
- policy: asking about refund, privacy, terms, trial, or billing policies
- tool: requesting a specific action like booking a demo, contacting support, etc.
- general: any other question or statement

User message: {user_input}

Respond with only one word: pricing, high_intent, policy, tool, or general"""

        response = llm.invoke(prompt, timeout=10)  # Shorter timeout for intent detection

        if not response or not response.content:
            return "general"

        # Handle different response formats
        if isinstance(response.content, list):
            # Extract text from list format
            text = ""
            for item in response.content:
                if isinstance(item, dict) and 'text' in item:
                    text += item['text']
                elif isinstance(item, str):
                    text += item
            text = text.strip().lower()
        else:
            text = response.content.strip().lower()

        if "pricing" in text:
            return "pricing"
        elif "high_intent" in text:
            return "high_intent"
        elif "policy" in text:
            return "policy"
        elif "tool" in text:
            return "tool_request"
        else:
            return "general"

    except Exception as e:
        print(f"⚠ API Error in intent detection: {str(e)[:100]}...")
        print("🔄 Falling back to keyword-based detection")
        # Fallback to simple keyword detection
        user_lower = user_input.lower()
        
        if any(word in user_lower for word in ["price", "cost", "plan", "pricing", "how much"]):
            return "pricing"
        elif any(word in user_lower for word in ["refund", "privacy", "terms", "trial", "billing"]):
            return "policy"
        elif any(word in user_lower for word in ["buy", "purchase", "start", "interested", "want", "sign up"]):
            return "high_intent"
        elif any(word in user_lower for word in ["demo", "book", "schedule", "contact", "support"]):
            return "tool_request"
        else:
            return "general"

# ============================================
# MAIN AGENT LOGIC WITH ALL FEATURES
# ============================================
def agent(user_input):
    global lead_stage, lead_data, lead_substage

    print("DEBUG: Inside agent")

    # Add to conversation memory
    conversation_memory.add("user", user_input)

    # Lead flow - Enhanced multi-step capture
    if lead_stage > 0:
        print("DEBUG: Lead stage:", lead_stage, "substage:", lead_substage)

        if lead_stage == 1:
            if lead_substage == 0:
                # Step 1: Get name
                lead_data["name"] = user_input
                lead_substage = 1
                return "Great! What's your email address?"
            
            elif lead_substage == 1:
                # Step 2: Get email
                lead_data["email"] = user_input
                lead_substage = 2
                return "Perfect! What's your phone number? (or type 'skip' to skip)"
            
            elif lead_substage == 2:
                # Step 3: Get phone (optional)
                if user_input.lower() != "skip":
                    lead_data["phone"] = user_input
                lead_substage = 3
                return "Which platform do you primarily create content on? (YouTube, TikTok, Instagram, etc.)"
            
            elif lead_substage == 3:
                # Step 4: Get platform
                lead_data["platform"] = user_input
                lead_substage = 4
                return "What company do you work for? (or type 'skip' to skip)"
            
            elif lead_substage == 4:
                # Step 5: Get company (optional)
                if user_input.lower() != "skip":
                    lead_data["company"] = user_input
                lead_substage = 5
                return "What are you most interested in? (e.g., video automation, AI captions, scheduling)"
            
            elif lead_substage == 5:
                # Step 6: Get interest and complete
                lead_data["interest"] = user_input
                
                # Capture the lead
                mock_lead_capture(
                    lead_data["name"],
                    lead_data["email"],
                    lead_data["platform"],
                    lead_data.get("phone"),
                    lead_data.get("company"),
                    lead_data.get("interest")
                )

                # Reset
                lead_stage = 0
                lead_substage = 0
                lead_data = {"name": None, "email": None, "platform": None, "phone": None, "company": None, "interest": None}
                
                return "🎉 You're all set! Our team will contact you within 24 hours. Check your email for confirmation!"

    # Intent detection
    print("DEBUG: Detecting intent...")
    intent = detect_intent(user_input)
    print("DEBUG: Intent =", intent)

    # Greeting
    if intent == "greeting":
        response = "Hello! 👋 Welcome to AutoStream. How can I help you today?"
        conversation_memory.add("bot", response)
        return response

    # Policy questions
    elif intent == "policy":
        policy_answer = handle_policy_question(user_input)
        if policy_answer:
            conversation_memory.add("bot", policy_answer)
            return policy_answer
        return "I couldn't find that policy information. Please contact support for more details."

    # Tool execution
    elif intent == "tool_request":
        user_lower = user_input.lower()
        
        if "demo" in user_lower or "book" in user_lower or "schedule" in user_lower:
            lead_stage = 1
            lead_substage = 0
            return "I'd be happy to book a demo for you! Let's start. What's your name?"
        
        elif "support" in user_lower or "help" in user_lower:
            result = tool_executor.execute("get_support", {})
            response = f"📞 Support Information:\n"
            response += f"Email: {result['data']['email']}\n"
            response += f"Phone: {result['data']['phone']}\n"
            response += f"Hours: {result['data']['hours']}"
            conversation_memory.add("bot", response)
            return response
        
        elif "contact" in user_lower or "call" in user_lower:
            lead_stage = 1
            lead_substage = 0
            return "Let me help you get in touch with us! What's your name?"
        
        else:
            response = "I can help you with: booking a demo, contacting support, or sending an email. What would you like?"
            conversation_memory.add("bot", response)
            return response

    # Pricing / General → RAG
    elif intent in ["pricing", "general"]:
        try:
            print("DEBUG: Calling RAG...")

            result = query_qa_chain(user_input)

            print("DEBUG: RAG result:", result)
            
            conversation_memory.add("bot", result)
            return result

        except Exception as e:
            print("ERROR in RAG:", e)
            response = "Sorry, I had trouble retrieving information."
            conversation_memory.add("bot", response)
            return response

    # High intent
    elif intent == "high_intent":
        lead_stage = 1
        lead_substage = 0
        return "That's great! Let's get started. What's your name?"

    # Fallback
    response = "I'm here to help! Ask me about pricing, features, policies, or say 'book a demo' to get started."
    conversation_memory.add("bot", response)
    return response


# ============================================
# ENHANCED MAIN LOOP
# ============================================
print("\n" + "="*60)
print(" 🤖 AutoStream AI Agent Ready!")
print("="*60)
print("Type 'exit' to quit, or try:")
print("  • 'hello' - for greeting")
print("  • 'what is the price' - for pricing info")
print("  • 'I want to buy' - to start lead capture")
print("  • 'book a demo' - to schedule a demo")
print("  • 'refund policy' - for policy questions")
print("  • 'support' - for help")
print("  • 'memory' - to see conversation history")
print("  • 'tools' - to see available tools")
print("  • 'demo lead' - to see lead capture demo")
print("="*60 + "\n")

try:
    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() == "exit":
                print("Goodbye! ")
                break
            
            # Special commands
            elif user_input.lower() == "memory":
                print("\n" + "="*50)
                print(" 📜 CONVERSATION MEMORY")
                print("="*50)
                print(conversation_memory.get_context())
                print("="*50 + "\n")
                continue
            
            elif user_input.lower() == "tools":
                print("\n" + "="*50)
                print(" 🔧 AVAILABLE TOOLS")
                print("="*50)
                for tool in tool_executor.get_available_tools():
                    print(f"  • {tool}")
                print("="*50 + "\n")
                continue
            
            elif user_input.lower() == "demo lead":
                demonstrate_lead_capture()
                continue

            response = agent(user_input)
            print(f"Bot: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"ERROR in chat loop: {e}")
            continue
except Exception as e:
    print(f"FATAL ERROR: {e}")
    import traceback
    traceback.print_exc()