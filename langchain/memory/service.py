"""
We build a chatbot service. We have to compile following objectives:
1. each user conversation has to happen within unique session
2. per each user we want to store the users chat history
"""

from os import getenv
from dotenv import load_dotenv

load_dotenv()

from langgraph.checkpoint.memory import InMemorySaver

from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI


if __name__ == "__main__":
    checkpointer = InMemorySaver()
    llm = ChatGoogleGenerativeAI(
        model=getenv("GOOGLE_CHAT_MODEL"), api_key=getenv("GOOGLE_API_KEY")
    )

    agent = create_agent(model=llm, checkpointer=checkpointer)

    thread_id = "session_1"
    config = {"configurable": {"thread_id": thread_id}}

    print(f"--- Chatbot started (Session: {thread_id}) ---")
    print("Type 'exit' or 'quit' to stop.\n")

    # 3. Бесконечный цикл общения
    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        # Отправляем сообщение агенту
        agent.invoke({"messages": [{"role": "user", "content": user_input}]}, config)

        # 4. Извлекаем и выводим содержимое памяти
        state = agent.get_state(config)
        messages = state.values["messages"]

        print("\n" + "=" * 30)
        print(f"CURRENT MEMORY (Messages: {len(messages)})")
        for i, msg in enumerate(messages):
            # Отображаем роль (User/AI) и начало текста сообщения
            role = msg.__class__.__name__.replace("Message", "")
            print(f"{i}. [{role}]: {msg.content[:50]}...")
        print("=" * 30 + "\n")

        # Печатаем последний ответ бота
        print(f"AI: {messages[-1].content}\n")
