import os
import google.generativeai as genai

# Configure the Gemini API with the API key
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

# List available models
models = genai.list_models()
for model in models:
    print(model.name)