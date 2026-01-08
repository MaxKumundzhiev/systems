from langchain_core.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder,
)


# PromptTemplate
template = PromptTemplate.from_template(
    template="Share interesting fact about {animal}"
)
# print(template)
prompt = template.format(animal="octopus")
# print(prompt)


# ChatPromptTemplate, involves roles
template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a patient tutor who explains things clearly."),
        ("human", "Can you explain {concept} like I'm five?"),
    ]
)
# print(template)
prompt = template.format_messages(concept="gravity")
# print(prompt)

# MessagesPlaceholder
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful career coach."),
        MessagesPlaceholder("conversation"),  # Dynamic history insertion
        ("human", "{current_question}"),
    ]
)

# Define history using proper message objects
conversation_history = [
    HumanMessage(content="How do I prepare for a job interview?"),
    AIMessage(
        content="Start by researching the company and practicing common questions."
    ),
]

formatted_messages = chat_prompt.format_messages(
    conversation=conversation_history,
    current_question="Should I send a thank-you email afterward?",
)

print(formatted_messages)
