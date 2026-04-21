import json

# Load knowledge base
with open("knowledge.json", "r") as f:
    knowledge = json.load(f)

# Memory
chat_history = []
lead_data = {"name": None, "email": None, "platform": None}
lead_stage = 0  # 0 = not started, 1 = name, 2 = email, 3 = platform

# Tool function
def mock_lead_capture(name, email, platform):
    print(f"\n✅ Lead captured successfully: {name}, {email}, {platform}\n")

# Intent Detection
def detect_intent(user_input):
    text = user_input.lower()

    if any(word in text for word in ["hi", "hello", "hey"]):
        return "greeting"
    elif any(word in text for word in ["price", "pricing", "cost", "plan"]):
        return "pricing"
    elif any(word in text for word in ["buy", "subscribe", "start", "want", "try"]):
        return "high_intent"
    else:
        return "general"

# RAG Retrieval
def get_pricing_info():
    basic = knowledge["pricing"]["basic"]
    pro = knowledge["pricing"]["pro"]

    return f"""
📦 Basic Plan:
- Price: {basic['price']}
- Features: {basic['features']}

🚀 Pro Plan:
- Price: {pro['price']}
- Features: {pro['features']}
"""

def get_policy_info():
    refund = knowledge["policies"]["refund"]
    support = knowledge["policies"]["support"]

    return f"""
📜 Policies:
- Refund: {refund}
- Support: {support}
"""

# Agent Response
def agent_response(user_input):
    global lead_stage, lead_data

    intent = detect_intent(user_input)

    # If already in lead capture flow
    if lead_stage > 0:
        if lead_stage == 1:
            lead_data["name"] = user_input
            lead_stage = 2
            return "Great! Please provide your email."

        elif lead_stage == 2:
            lead_data["email"] = user_input
            lead_stage = 3
            return "Awesome! Which platform do you create content on? (YouTube/Instagram/etc.)"

        elif lead_stage == 3:
            lead_data["platform"] = user_input

            # Call tool ONLY now
            mock_lead_capture(
                lead_data["name"],
                lead_data["email"],
                lead_data["platform"]
            )

            lead_stage = 0
            return "🎉 You're all set! Our team will contact you soon."

    # Normal flow
    if intent == "greeting":
        return "Hello! 👋 Welcome to AutoStream. How can I help you today?"

    elif intent == "pricing":
        return get_pricing_info()

    elif intent == "high_intent":
        lead_stage = 1
        return "That's great to hear! 😊 Let's get you started. What's your name?"

    else:
        return "I can help you with pricing, features, or getting started. What would you like to know?"

# Run chatbot
print("🤖 AutoStream AI Agent (type 'exit' to quit)\n")

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        print("Goodbye! 👋")
        break

    chat_history.append({"user": user_input})

    response = agent_response(user_input)

    chat_history.append({"bot": response})

    print("Bot:", response)