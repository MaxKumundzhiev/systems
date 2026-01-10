# Intro
Memory is a system that remembers information about previous interactions. For AI agents, memory is crucial because it lets them remember previous interactions, learn from feedback, and adapt to user preferences. As agents tackle more complex tasks with numerous user interactions, this capability becomes essential for both efficiency and user satisfaction.


There 2 major types of memory:
1. Short-term memory, or thread-scoped memory, tracks the ongoing conversation by maintaining message history within a session. LangGraph manages short-term memory as a part of your agent’s state. State is persisted to a database using a checkpointer so the thread can be resumed at any time. Short-term memory updates when the graph is invoked or a step is completed, and the State is read at the start of each step.

2. Long-term memory stores user-specific or application-level data across sessions and is shared across conversational threads. It can be recalled at any time and in any thread. Memories are scoped to any custom namespace, not just within a single thread ID. LangGraph provides stores (reference doc) to let you save and recall long-term memories.


# LangChain Types of Memory (Depricated)
- ConversationBufferMemory - object which stores and return all the messages as a list
- ConversationBufferWindowMemory - object which stores and return k messages as a list, where k is defined as window
- ConversationSummaryMemory - object which stores and return the summary of messages as a list (by each interaction it perform compression over stored messages)
- ConversationSummaryBufferMemory - object which stores and return k tokens of the summary of messages 