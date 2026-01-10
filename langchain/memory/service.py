"""
We build a chatbot service. We have to compile following objectives:
1. each user conversation has to happen within unique session
2. per each user we want to store the users chat history
"""

from dotenv import load_dotenv
import google.genai as genai

load_dotenv()


client = genai.Client()
model = "gemini-2.5-flash-lite"


from langgraph.store.memory import 



# response = client.models.generate_content(
#     model=model, contents="Привет! Расскажи коротко о себе."
# )
# print(response.text)
