"""
assume we have a review service.
it takes customer review and has to parse a particular entities.
"""

from dotenv import load_dotenv
from typing import List
from pydantic import BaseModel, Field

# Import Gemini instead of OpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate


class Review(BaseModel):
    gift: bool = Field(
        description="Was the item purchased as a gift? True if yes, False if no/unknown.",
    )
    delivery: int = Field(
        description="Days for product to arrive. Output -1 if not found.",
    )
    price: List[str] = Field(
        description="Extract any sentences about price/value as a list.",
    )


class Interface:

    def __init__(self, model_name: str = "gemini-2.5-flash-lite") -> None:
        self.reviews: List[Review] = []

        # 1. Initialize Gemini
        # Note: Ensure GOOGLE_API_KEY is set in your environment variables
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0,
            convert_system_message_to_human=True,  # Helper for older Gemini models
        )

        # 2. Bind structured output
        # Gemini uses 'json_schema' method by default in newer LangChain versions
        self.structured_llm = self.llm.with_structured_output(Review)

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a specialized data extraction bot. Extract review details accurately.",
                ),
                ("human", "{input}"),
            ]
        )

        self.chain = self.prompt | self.structured_llm

    def process_review(self, text: str) -> Review:
        result = self.chain.invoke({"input": text})
        self.reviews.append(result)
        return result


# --- Running the code ---
if __name__ == "__main__":
    load_dotenv()
    interface = Interface()

    review_data = "I got this for my mom's garden. It arrived in 2 days. Total bargain for the price!"
    output = interface.process_review(review_data)

    print(f"Gift: {output.gift}")
    print(f"Delivery: {output.delivery} days")
    print(f"Price mentions: {output.price}")
