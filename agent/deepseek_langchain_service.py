# pip3 install langchain_openai
# python3 deepseek_langchain.py
import getpass
import logging
import os
from typing import Any

import pandas as pd
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_deepseek import ChatDeepSeek
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool

from config import settings
from sales.customer_management import CustomerManager
from sales.customer_schema import CustomerCreate

# Uses the pickle module for serialization
# Make sure that you're only de-serializing trusted data
# (e.g., payloads that you have serialized yourself).
# Or implement a custom serializer.


logger = logging.getLogger(__name__)
model = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0.4,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)

if not os.getenv("DEEPSEEK_API_KEY"):
    os.environ["DEEPSEEK_API_KEY"] = getpass.getpass("Enter your DeepSeek API key: ")


class DeepSeekLCService:
    def __init__(self, connection_pool: ConnectionPool):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.checkpointer = PostgresSaver(conn=connection_pool)
        self.llm = create_agent(
            checkpointer=self.checkpointer,
            model=model,  # intalled model="claude-sonnet-4-5-20250929",
            tools=[load_products, set_customer_contact, get_customer_by_phone_number],
            system_prompt="You are a helpful supermarket salesman.Be concise and accurate."
            "You are selling  through whatsapp messages."
            "client_phone is provided in the user message prefix <client_phone>."
            "retrieve customer data using the phone number provided in the user message prefix <client_phone>. with the tool get_customer_by_phone_number. using client_phone as argument"
            "if do not know the customer name, Always ask for the customer's name at the beginning of the conversation,"
            "The supermarket is located in Brazil and sells groceries and household items."
            "Never ask for the customer phone number, it is provided in the user message<client_phone>."
            "load products and use it to answer customer questions about products and prices."
            "ask custommer name his name and use tool set_customer_contact to store it with the telephone number provided by in the begining of the user msg<client_phone>."
            "if the customer ask for product list, load the product list use the tool load_products and provide options"
            "The supermarket name is Bom preço Supermercados."
            "It is located at 9 de Julho Avenue, 1234, São Paulo, SP, Brazil."
            "DO not say the product list with prices befeore the customer ask for it."
            "If a product is not in stock, inform the customer politely. and offer a similar product if possible."
            "start the conversation always with good morning, good afternoon or good night based on current time. gmt -3 timezone."
            "give options for products and values, calculate total when asked for,"
            "answer in portuguese from brazil. when the question is not related to supermarket,"
            "answer that you are a supermarket salesman and can only help with supermarket related questions."
            "when providing product options, always include prices and quantities."
            "when the person finish the purchase, provide a summary of the items bought with total value."
            "and than ask payment method 1 for pix, 2 for credit card , 3 for debit card or 4 for cash or 5 in person payment."
            "ask the address for delivery and if the person want delivery."
            "if payment method is pix, generate a fake pix code."
            "always ask how can you help the customer.",
        )

    async def chat_completion(
        self,
        messages,
        session_id,
        client_phone,
        stream=False,
        prompt="",
    ):
        # print("Invoking DeepSeek LLM via LangChain...")
        # print("Messages:", messages)
        try:
            response = self.llm.invoke(
                {
                    "messages": [
                        {
                            "role": message.role,
                            "content": f"<{client_phone}>" + message.content,
                        }
                        for message in messages
                    ]
                },
                {"configurable": {"thread_id": client_phone}},
            )
            # print(response)
            # print("Response content:", response["messages"][-1])
            return response["messages"][-1].content
        except Exception as e:
            logger.error(f"DeepSeekLCService chat_completion error: {str(e)}")
            raise


customerManager = CustomerManager()


@tool
def load_products():
    """
    Load the product list from the local Excel file 'produtos.xlsx'.

    This function return the  product list for the supermarket salesman.

    Returns:
        pandas.DataFrame: DataFrame containing product data loaded from
        'produtos.xlsx'.

    Raises:
        FileNotFoundError: If 'produtos.xlsx' does not exist in the current
            working directory.
        ValueError, XLRDError, or other pandas-related exceptions raised by
            pandas.read_excel when the file cannot be parsed.

    Notes:
        - The path to the Excel file is hard-coded; change the implementation
          if you need to load from a different location or allow caller-specified paths.
        - The caller is responsible for importing pandas as pd before calling
          this function (or the module should import it).
        - Consider adding validation of expected columns after loading if the
          consumer relies on specific fields.
    """
    df = pd.read_excel("produtos.xlsx")
    return df


@tool
def set_customer_contact(name: str, cellphone: str) -> str:
    """
    Store the customer's name for personalized interactions.
    Args:
        name (str): The customer's name
        cellphone (str): The customer's phone number
    Returns:
        str: Confirmation message
    """
    try:
        customerManager.create_customer(
            CustomerCreate(
                name=name,
                cellphone=cellphone,
            )
        )
        logger.info(f"Stored customer name: {name} for cellphone: {cellphone}")
        return f"Customer name '{name}' has been stored."
    except Exception as e:
        logger.error(f"Error storing customer: {e}")
        return f"Error storing customer information: {str(e)}"


@tool
def get_customer_by_phone_number(client_phone: str) -> Any | None:
    """
    Retrieve customer by phone number.
    Args:
        phone_number (str): Customer's phone number
    Returns:
        Any | None: Customer object or None if not found
    """
    try:
        customer = customerManager.get_customer(client_phone)
        logger.info(f"Retrieved customer: {client_phone} -> {customer}")
        return customer
    except Exception as e:
        logger.error(f"Error retrieving customer: {e}")
        return None
