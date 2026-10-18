
import ollama

MODEL_NAME = "llama3.2"


def generate_response(
    prompt: str,
    system_prompt: str = "You are a helpful AI assistant.",
) -> str:
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        format="json",
        options={
            "num_predict": 2048,
            "temperature": 0,
        },
    )

    return response["message"]["content"]
