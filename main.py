import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader

# Load env
load_dotenv()

# LLM
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)

# Load knowledge base
loader = TextLoader("knowledge.json")
documents = loader.load()

# Split text
text_splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=50)
docs = text_splitter.split_documents(documents)

# Embeddings + Vector DB
embeddings = GoogleGenerativeAIEmbeddings(model="text-embedding-gecko")
vectorstore = FAISS.from_documents(docs, embeddings)

retriever = vectorstore.as_retriever()

# Memory (simple list to store conversation history)
chat_history = []

# RAG Chain using simple invocation
def query_qa_chain(question):
    docs = retriever.get_relevant_documents(question)
    context = "\n".join([doc.page_content for doc in docs])
    prompt = f"""Using the following context, answer the question.
    
Context:
{context}

Question: {question}

Answer:"""
    response = llm.invoke(prompt).content
    return response

# Lead storage
lead_data = {"name": None, "email": None, "platform": None}
lead_stage = 0

# Tool
def mock_lead_capture(name, email, platform):
    print(f"\n Lead captured successfully: {name}, {email}, {platform}\n")

# Intent Detection using LLM
def detect_intent(user_input):
    prompt = f"""
    Classify the intent of this message into one of:
    - greeting
    - pricing
    - high_intent
    - general

    Message: {user_input}

    Only return the intent label.
    """

    response = llm.invoke(prompt).content.strip().lower()
    return response

# Main Agent Logic
def agent(user_input):
    global lead_stage, lead_data

    # If in lead collection
    if lead_stage > 0:
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
            return "🎉 You're all set! Our team will contact you soon."

    # Detect intent via LLM
    intent = detect_intent(user_input)

    if "greeting" in intent:
        return "Hello!  Welcome to AutoStream. How can I help you?"

    elif "pricing" in intent:
        result = query_qa_chain(user_input)
        return result

    elif "high_intent" in intent:
        lead_stage = 1
        return "That's great!  Let's get started. What's your name?"

    else:
        result = query_qa_chain(user_input)
        return result


# Run loop
print("🤖 AutoStream AI Agent (LangChain + RAG)\n")

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        print("Goodbye! ")
        break

    response = agent(user_input)
    print("Bot:", response)