import os
from dotenv import load_dotenv
import openai

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Bạn chưa đặt OPENAI_API_KEY trong .env")

openai.api_key = api_key

class OpenAIClient:
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.model_name = model_name
        self.client = openai.OpenAI(api_key=api_key)

    async def generate_text(self, prompt: str, max_output_tokens: int = 256) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_output_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error generating text with OpenAI: {str(e)}")