import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
api_key = os.getenv("CLAUDE_API_KEY")
if not api_key:
    raise ValueError("Bạn chưa đặt CLAUDE_API_KEY trong .env")

class ClaudeClient:
    def __init__(self, model_name: str = "claude-3-sonnet-20240229"):
        self.model_name = model_name
        self.client = Anthropic(api_key=api_key)

    async def generate_text(self, prompt: str, max_output_tokens: int = 2048) -> str:
        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=max_output_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return response.content[0].text
        except Exception as e:
            raise Exception(f"Error generating text with Claude: {str(e)}")
