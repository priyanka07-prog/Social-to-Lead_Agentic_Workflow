import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load env
load_dotenv(dotenv_path=".env")

# Configure API
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

print("Available models:")
print("-" * 50)

for model in genai.list_models():
    print(f"- {model.name}")
    if hasattr(model, 'supported_generation_methods'):
        print(f"  Methods: {model.supported_generation_methods}")
