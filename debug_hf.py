import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

token = os.getenv("HUGGINGFACE_API_TOKEN")
model_id = "mistralai/Mistral-7B-Instruct-v0.2"

print(f"Testing with huggingface_hub library...")
client = InferenceClient(model=model_id, token=token)

try:
    print(f"Testing basic text generation...")
    response = client.text_generation("Hi, provide a 5 word response.", max_new_tokens=10)
    print(f"Success! Response: {response}")
except Exception as e:
    print(f"Error with huggingface_hub: {str(e)}")

try:
    print(f"\nTesting chat completion...")
    chat_response = client.chat_completion(
        messages=[{"role": "user", "content": "Hi"}],
        max_tokens=10
    )
    print(f"Success! Chat Response: {chat_response.choices[0].message.content}")
except Exception as e:
    print(f"Error with chat completion: {str(e)}")
