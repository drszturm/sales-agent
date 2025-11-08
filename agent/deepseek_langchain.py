# pip3 install langchain_openai
# python3 deepseek_langchain.py
import logging

import pandas as pd
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_deepseek import ChatDeepSeek
from config import settings
import getpass
import os
# Read entire XLSX file

logger = logging.getLogger(__name__)
model = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)

if not os.getenv("DEEPSEEK_API_KEY"):
    os.environ["DEEPSEEK_API_KEY"] = getpass.getpass("Enter your DeepSeek API key: ")


class DeepSeekLCService:
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.llm = create_agent(
            checkpointer=InMemorySaver(),
            model=model,  # intalled model="claude-sonnet-4-5-20250929",
            tools=[load_products, set_customer_contact, get_actual_phone_number],
            system_prompt="You are a helpful supermarket salesman.Be concise and accurate."
            "if do not know the customer name, Always ask for the customer's name at the beginning of the conversation,"
            "The supermarket is located in Brazil and sells groceries and household items."
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

    def chat_completion(
        self,
        messages,
        session_id,
        client_phone,
        stream=False,
        prompt="",
    ):
        # print("Invoking DeepSeek LLM via LangChain...")
        # print("Messages:", messages)
        response = self.llm.invoke(
            {
                "messages": [
                    {
                        "role": message.role,
                        "content": f"<{session_id}+{client_phone}>" + message.content,
                    }
                    for message in messages
                ]
            },
            {"configurable": {"thread_id": client_phone}},
        )
        # print(response)
        print("Response content:", response["messages"][-1])
        return response["messages"][-1]


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


def set_customer_contact(name: str, cellphone: str) -> str:
    """
    Store the customer's name for personalized interactions.

    This function simulates storing the customer's name, which can be used
    later in conversations to enhance user experience.

    Args:
        name (str): The name of the customer to store.

    Returns:
        str: Confirmation message indicating the name has been stored.
    """
    # In a real implementation, this could store the name in a database
    # or session context. Here, we simply return a confirmation message.
    logging.info(f"Storing customer name: {name} for cellphone: {cellphone}")
    return f"Customer name '{name}' has been stored."


def get_actual_phone_number() -> str:
    """
    Retrieve the actual phone number of the customer.

    This function simulates retrieving the customer's phone number,
    which can be used for contact or identification purposes.

    Returns:
        str: The customer's phone number.
    """
    # In a real implementation, this could retrieve the phone number from
    # session context or request metadata. Here, we return a placeholder.
    return "+55 11 91234-5678"


def get_customer_by_phone_number(phone_number: str) -> str | None:
    """
    Retrieve the customer's name based on their phone number.

    This function simulates looking up a customer's name using their
    phone number, which can be useful for personalized interactions.

    Args:
        phone_number (str): The phone number of the customer.
    Returns:
        str: The name of the customer associated with the phone number.
        None: If no customer is found for the given phone number.
    """

    # In a real implementation, this could query a database.
    # Here, we return a placeholder name.
    return "David"


deepseek_lc_service = DeepSeekLCService()
