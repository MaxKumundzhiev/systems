<<<<<<< Updated upstream
# Component Overview
<img width="719" height="516" alt="Screenshot 2026-01-10 at 12 41 43" src="https://github.com/user-attachments/assets/745465a6-e008-4405-8b6b-5497bc859d5b" />


# Memory
in general LangChain (LangGraph) on a conceptual level destingiushs 2 types of memory:
1. Short-term memory
2. Long-term memory

Commonly `short-term` memory stands for RAM memory and `long-term` memory for persisted memory within a particula percisted storage.

### Short term memory
Short term memory lets your application remember previous interactions within a single thread or conversation.
A thread organizes multiple interactions in a session, similar to the way email groups messages in a single conversation.


To manage short term memory use abstraction InMemorySaver (its a hashmap or dict in python)
```python
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver  


agent = create_agent(
    "gpt-5",
    tools=[get_user_info],
    checkpointer=InMemorySaver(),  
)

agent.invoke(
    {"messages": [{"role": "user", "content": "Hi! My name is Bob."}]},
    {"configurable": {"thread_id": "1"}},  
)
```
