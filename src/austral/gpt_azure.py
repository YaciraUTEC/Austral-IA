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
embedding_deplyment_name = os.getenv("AZURE_EMBEDDING_DEPLOYMENT")

def extraer_objeto_gpt(historial: list, pregunta: str) -> str:
    """
    Usa GPT para identificar el objeto principal de la conversación.
    """
    prompt_objeto = (
        "Dada la siguiente conversación, identifica el objeto principal o tema al que se refiere la última pregunta del usuario. "
        "Devuelve solo el objeto o tema, sin explicación adicional.\n\n"
        "Historial de la conversación:\n"
    )
    for mensaje in historial:
        prompt_objeto += f"{mensaje['role']}: {mensaje['content']}\n"
    prompt_objeto += f"user: {pregunta}\nObjeto:"

    mensajes = [
        {"role": "system", "content": "Eres un extractor de temas. Devuelve solo el objeto o tema principal de la última pregunta del usuario."},
        {"role": "user", "content": prompt_objeto}
    ]
    try:
        response = client.chat.completions.create(
            model=deployment_name,
            messages=mensajes,
            temperature=0.0,
            max_tokens=20
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return ""

def chat_completion(mensajes: list) -> str:
    """
    Envía una lista de mensajes (historial conversacional) al modelo de Azure OpenAI y retorna la respuesta.
    """
    try:
        response = client.chat.completions.create(
            model=deployment_name,
            messages=mensajes,
            temperature=0.1,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error al procesar la solicitud: {str(e)}"

    

def embed_text(text: str) -> list[list[float]]:
    try:
        response = client.embeddings.create(
            model=embedding_deplyment_name,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        raise RuntimeError(f"Error al generar embedding: {str(e)}")