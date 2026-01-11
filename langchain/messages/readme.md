# Messages
Messages are the fundamental unit of context for models in LangChain. They represent the input and output of models, carrying both the content and metadata needed to represent the state of a conversation when interacting with an LLM.

Messages contains:
1. Role - Identifies the message type (e.g. system, user)
2. Content - Represents the actual content of the message (like text, images, audio, documents, etc.)
3. Metadata - Optional fields such as response information, message IDs, and token usage

```python
# usage
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, AIMessage, SystemMessage

model = init_chat_model("gpt-5-nano")

system_msg = SystemMessage("You are a helpful assistant.")
human_msg = HumanMessage("Hello, how are you?")

messages = [system_msg, human_msg]
response = model.invoke(messages)  # Returns AIMessage
```