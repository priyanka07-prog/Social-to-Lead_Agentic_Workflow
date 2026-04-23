# AutoStream Conversational AI Agent

This project is a Conversational AI Agent built for a fictional SaaS company, AutoStream.

The agent can:
- Understand user intent (greeting, pricing, high intent)
- Retrieve information using RAG (Retrieval Augmented Generation)
- Capture user leads using a tool-based workflow

**⚙️ Tech Stack**
- Python 3.11
- LangChain
- Google Gemini (LLM)
- FAISS (Vector Store)


### *Architecture Explanation *

This project uses a modular AI agent architecture built with LangChain and Gemini.

The system consists of three main components:

1. Intent Detection:
User input is analyzed to classify intent into greeting, pricing, high intent, or general queries. A hybrid approach combining rule-based logic and LLM inference is used for better accuracy.

2. Retrieval-Augmented Generation (RAG):
A local knowledge base containing pricing and policy information is embedded using vector embeddings. FAISS is used as the vector store, and relevant chunks are retrieved based on user queries. The LLM then generates accurate responses grounded in this data.

3. Tool Execution (Lead Capture):
When high intent is detected, the agent initiates a structured flow to collect user details such as name, email, and platform. The lead capture tool is triggered only after all required inputs are collected, ensuring controlled execution.

Conversation memory is maintained using LangChain memory to preserve context across multiple turns.

**How to Run**
1. Clone the repository
2. Create a virtual environment:
   python -m venv venv

3. Activate it:
   venv\Scripts\activate

4. Install dependencies:
   pip install -r requirements.txt

5. Add your Gemini API key in .env:
   GOOGLE_API_KEY=your_api_key_here

6. Run the project:
   python main.py

**WhatsApp Integration (Webhook Explanation)**

   To integrate this agent with WhatsApp, a webhook-based architecture can be used.

1. Use WhatsApp Business API (via providers like Twilio or Meta Cloud API).
2. Configure a webhook endpoint using a backend framework like FastAPI or Flask.
3. Incoming user messages are sent to the webhook.
4. The webhook forwards the message to the AI agent.
5. The agent processes the input and returns a response.
6. The response is sent back to the user via the WhatsApp API.

This allows real-time conversational interaction with users on WhatsApp.

**Demo**

A demo video is included showing:
- Greeting response
- Pricing retrieval using RAG
- High intent detection
- Lead capture flow
- Tool execution

(https://drive.google.com/file/d/1jaUpyn05jhoo8061qkvPiS16Ev5fbujR/view?usp=drive_link)

## 🎥 Demo Video

[Click here to watch demo]

<video controls src="20260423-0835-48.5003012.mp4" title="Title"></video>