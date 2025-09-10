import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Bạn chưa đặt GEMINI_API_KEY trong .env")

genai.configure(api_key=api_key)

class GeminiClient:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.model = genai.GenerativeModel(model_name)

    async def generate_text(self, prompt: str, max_output_tokens: int = 256) -> str:
        response = self.model.generate_content(prompt)
        return response.text
