import os
from typing import Dict, List
from uuid import uuid4
from dotenv import load_dotenv

from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import (
    InMemoryChatMessageHistory,
    BaseChatMessageHistory,
)

load_dotenv()


class HuggingFaceChatbot:
    def __init__(self, model_id: str = "meta-llama/Llama-3.2-3B-Instruct"):
        self.llm = HuggingFaceEndpoint(
            model=model_id,
            task="text-generation",
            max_new_tokens=50,
            temperature=0.0,
        )
        self.chat_model = ChatHuggingFace(llm=self.llm)
        self.store: Dict[str, InMemoryChatMessageHistory] = {}
        self.chain = self._build_chain()

        self.agent = RunnableWithMessageHistory(
            self.chain,
            self._get_session_history,
            input_messages_key="input",
            history_messages_key="history",
        )

    def _build_chain(self):
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful AI assistant. Answer concisely."),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}"),
            ]
        )
        return prompt | self.chat_model

    def _get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self.store:
            self.store[session_id] = InMemoryChatMessageHistory()
        return self.store[session_id]

    def ask(self, user_input: str, session_id: str) -> str:
        """Sends a message to the bot and returns the text response."""
        config = {"configurable": {"session_id": session_id}}
        response = self.agent.invoke({"input": user_input}, config=config)
        return response.content

    def get_memory_log(self, session_id: str) -> List[str]:
        """Returns a formatted list of the current memory for a session."""
        history = self._get_session_history(session_id)
        return [f"{msg.type.upper()}: {msg.content}" for msg in history.messages]


if __name__ == "__main__":
    bot = HuggingFaceChatbot()
    my_session = str(uuid4())

    print(f"Chat Session Started: {my_session}\n")

    while True:
        text = input("You: ").strip()
        if text.lower() in ["exit", "quit"]:
            break

        if text.lower() == "show memory":
            print("\n--- MEMORY ---")
            print("\n".join(bot.get_memory_log(my_session)))
            print("--------------\n")
            continue

        reply = bot.ask(text, my_session)
        print(f"AI: {reply}\n")
