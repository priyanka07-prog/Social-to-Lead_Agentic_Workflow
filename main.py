import os
import json
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

# Simple QA function without embeddings
def query_qa_chain(question):
    try:
        prompt = f"""You are a helpful assistant. Use the following knowledge base to answer the question.
    
Knowledge Base:
{knowledge_text}

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

# Lead storage
lead_data = {"name": None, "email": None, "platform": None}
lead_stage = 0

# Tool
def mock_lead_capture(name, email, platform):
    print(f"\n Lead captured successfully: {name}, {email}, {platform}\n")

# Intent Detection using LLM
def detect_intent(user_input):
    try:
        # Check for greeting first based on user input
        if any(word in user_input.lower() for word in ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"]):
            return "greeting"

        # For other intents, use LLM to analyze
        prompt = f"""Analyze the user's message and classify their intent. Choose from:
- pricing: asking about costs, prices, plans, or pricing information
- high_intent: showing interest in buying, purchasing, or getting started
- general: any other question or statement

User message: {user_input}

Respond with only one word: pricing, high_intent, or general"""

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
        else:
            return "general"

    except Exception as e:
        print(f"⚠ API Error in intent detection: {str(e)[:100]}...")
        print("🔄 Falling back to keyword-based detection")
        # Fallback to simple keyword detection
        if any(word in user_input.lower() for word in ["price", "cost", "plan", "pricing", "how much"]):
            return "pricing"
        elif any(word in user_input.lower() for word in ["buy", "purchase", "start", "interested", "want", "sign up"]):
            return "high_intent"
        else:
            return "general"

# Main Agent Logic
def agent(user_input):
    global lead_stage, lead_data

    print("DEBUG: Inside agent")

    # Lead flow
    if lead_stage > 0:
        print("DEBUG: Lead stage:", lead_stage)

        if lead_stage == 1:
            lead_data["name"] = user_input
            lead_stage = 2
            return "Great! Please provide your email."

        elif lead_stage == 2:
            lead_data["email"] = user_input
            lead_stage = 3
            return "Awesome! Which platform do you create content on?"

        elif lead_stage == 3:
            lead_data["platform"] = user_input

            mock_lead_capture(
                lead_data["name"],
                lead_data["email"],
                lead_data["platform"]
            )

            lead_stage = 0
            return "You're all set! Our team will contact you soon."

    # Intent detection
    print("DEBUG: Detecting intent...")
    intent = detect_intent(user_input)
    print("DEBUG: Intent =", intent)

    # Greeting
    if intent == "greeting":
        return "Hello!  Welcome to AutoStream. How can I help you?"

    # Pricing / General → RAG
    elif intent in ["pricing", "general"]:
        try:
            print("DEBUG: Calling RAG...")

            result = query_qa_chain(user_input)

            print("DEBUG: RAG result:", result)

            return result

        except Exception as e:
            print("ERROR in RAG:", e)
            return "Sorry, I had trouble retrieving information."

    # High intent
    elif intent == "high_intent":
        lead_stage = 1
        return "That's great! Let's get started. What's your name?"

    # Fallback
    return "I'm here to help! Ask me about pricing or features."


# Run loop
print("\n" + "="*50)
print("🤖 AutoStream AI Agent Ready!")
print("Type 'exit' to quit, or try:")
print("- 'hello' for greeting")
print("- 'what is the price' for pricing info")
print("- 'I want to buy' for lead capture")
print("="*50 + "\n")

try:
    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() == "exit":
                print("Goodbye! 👋")
                break

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