# src/austral/gpt_azure.py
import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version=os.getenv("AZURE_OPENAI_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")

def chat_completion(prompt: str, contexto: str = "") -> str:
    try:
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {
                    "role": "system",
                    "content": contexto
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,  # Aumentamos ligeramente para permitir más análisis crítico
            max_tokens=1000  # Aumentamos para respuestas más detalladas
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error al procesar la solicitud: {str(e)}"