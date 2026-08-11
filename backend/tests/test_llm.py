from app.clients.llm_client import LLMClient
from app.core.settings import settings


client = LLMClient.get_client()

response = client.chat.completions.create(
    model=settings.AZURE_OPENAI_DEPLOYMENT,
    messages=[
        {
            "role": "system",
            "content": "You are a helpful AI assistant."
        },
        {
            "role": "user",
            "content": "Say hello in one sentence."
        }
    ],
)

print(response.choices[0].message.content)