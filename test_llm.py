import os
from dotenv import load_dotenv

print("Loading environment...")
load_dotenv(dotenv_path=".env")

api_key = os.getenv("GOOGLE_API_KEY")
print(f"API Key: {api_key[:10] if api_key else 'NOT FOUND'}...")

print("\nAttempting to import ChatGoogleGenerativeAI...")
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    print("Import successful!")
except Exception as e:
    print(f"Import failed: {e}")
    exit(1)

print("\nAttempting to initialize ChatGoogleGenerativeAI with gemini-1.5-pro...")
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0,
        timeout=60,
        api_key=api_key
    )
    print("Initialization successful!")
    
    print("\nTesting a simple query...")
    response = llm.invoke("Say hello")
    print(f"Response: {response.content}")
    
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
