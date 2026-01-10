"""
We build a chatbot service. We have to compile following objectives:
1. each user conversation has to happen within unique session
2. per each user we want to store the users chat history
"""

from os import getenv
from uuid import uuid4
from dotenv import load_dotenv

from datetime import datetime
from functools import cached_property

load_dotenv()

from langgraph.checkpoint.memory import InMemorySaver

from langchain.agents import create_agent
from langchain.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


class Agent:
    def __init__(self) -> None:
        self.model = getenv("GOOGLE_CHAT_MODEL")
        self.model_api_key = getenv("GOOGLE_API_KEY")
        self.checkpointer = InMemorySaver()
        self.llm = ChatGoogleGenerativeAI(model=self.model, api_key=self.model_api_key)

    @cached_property
    def inference(self):
        return create_agent(
            model=self.llm,
            tools=[],
            checkpointer=self.checkpointer,
            system_prompt=SystemMessage(
                "You are helpful and polite assistant. Your name is Foo."
            ),
        )


if __name__ == "__main__":
    agent = Agent().inference
    configuration = {"configurable": {"thread_id": uuid4()}}

    while True:
        user_query = input("You: ")
        response = agent.invoke(
            {"messages": [HumanMessage(content=user_query)]}, configuration
        )
        print(agent.get_state(configuration))
        print(response["messages"][-1].content)
