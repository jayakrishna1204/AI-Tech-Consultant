
import ollama

response = ollama.chat(
    model="llama3.2",
    messages=[
        {
            "role": "user",
            "content": "Explain RAG in simple words."
        }
    ]
)

print(response["message"]["content"])
