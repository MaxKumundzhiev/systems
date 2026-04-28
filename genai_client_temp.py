from os import environ
from google.genai import Client, types
from google.genai.types import HttpOptions

LITELLM_PROXY_URL = environ.get("LITELLM_PROXY_URL", "")
LITELLM_API_KEY = environ.get("LITELLM_API_KEY", "")


client = Client(
    api_key=LITELLM_API_KEY,
    http_options=HttpOptions(base_url=f"{LITELLM_PROXY_URL}/gemini"),
)

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="Hello, world!",
    config=types.GenerateContentConfig(
        http_options=HttpOptions(
            headers={
                "x-tlk-project-id": "ctash-test",
                "x-tlk-request-id": "12323asd",
            }
        )
    ),
)
print(response.text)
