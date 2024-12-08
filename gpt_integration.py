import os
from openai import OpenAI
from config import OPENAI_API_KEY, GPT_MODEL
from prompt import knowledge_base

# Configuración del cliente OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)


def prompt_creator(prompt):
    """
    Crea el mensaje para enviar a la API de OpenAI.
    """
    knowledge_related = knowledge_base()
    messages = [
        {"role": "system", "content": "Eres un experto en trading de criptodivisas."},
        {"role": "system", "content": f"Base de conocimiento relevante: {knowledge_related}"},
        {"role": "user", "content": prompt}
    ]
    return messages


def get_gpt_recommendation(prompt: str):
    """
    Solicita una recomendación a GPT utilizando el cliente actualizado.
    """
    final_prompt = prompt_creator(prompt)
    try:
        # Crear la solicitud a la API
        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=final_prompt,
            temperature=0.7,
            max_tokens=200,
        )
        # Obtener el contenido de la respuesta
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error al obtener recomendación de GPT: {e}")
        return None
