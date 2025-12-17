import httpx
import asyncio
import random
import torch
torch.set_num_threads(1)
from transformers import pipeline

# Generate answer based on the topic
def generate_answer():
    generator = pipeline('text-generation', model='distilgpt2')
    prompt = f"A resume has pros and cons as "
    res = generator(prompt, num_return_sequences=1, no_repeat_ngram_size=2, truncation=True)
    print(f"Generated text: {res[0]['generated_text']}")
    return res[0]['generated_text']


# Main async function to handle the HTTP request
async def run():
    try:
        # Use an asynchronous HTTP client
        async with httpx.AsyncClient() as client:
            while True:
                print("Starting to generate text...")
                generated_answer = generate_answer()

                try:
                    print("Sending request to server...")
                    # Send the answer as JSON
                    response = await client.post(
                        url="http://127.0.0.1:8000/answers/upload",
                        json={"text": generated_answer}  # Correct way to send JSON
                    )

                    # Check if the response is successful
                    response.raise_for_status()
                    print(f"Response status: {response.status_code}, Response data: {response.json()}")  # Print response for debugging

                except httpx.RequestError as e:
                    print(f"HTTP request failed: {e}")
                
                print("Waiting for next request...")
                # Optional: Add delay between requests if needed (e.g., 1 second)
                await asyncio.sleep(random.uniform(1, 10))

    except Exception as e:
        print(f"Error in async run function: {e}")


# Entry point for the script
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(run())  # Correct the function call by adding parentheses
    loop.run_forever()
