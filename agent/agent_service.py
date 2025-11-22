# python3 deepseek_langchain.py
import logging
from typing import Any
import pandas as pd
import httpx
from agent.claude_langchain import ClaudeLCService
from psycopg_pool import ConnectionPool
from langgraph.checkpoint.postgres import PostgresSaver
from langchain.tools import tool
from agent.deepseek_langchain_service import DeepSeekLCService
from agent.gemini_langchain import GoogleLCService
from config import settings
from sales.customer_management import CustomerManager
from sales.customer_schema import CustomerCreate
from langchain.tools import tool

connection_pool = ConnectionPool(
    conninfo=f"postgresql://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:5432/{settings.DB_NAME}?sslmode=disable",
    max_size=20,
    kwargs={"autocommit": True},
)


checkpointer = PostgresSaver(conn=connection_pool)
customer_manager = CustomerManager()
# Uses the pickle module for serialization
# Make sure that you're only de-serializing trusted data
# (e.g., payloads that you have serialized yourself).
# Or implement a custom serializer.
# checkpointer = PostgresSaver(conn=pool)


logger = logging.getLogger(__name__)


prompt = "You are a helpful supermarket salesman.Be concise and accurate."
"client_phone is provided in the user message prefix <client_phone>."
"Fruits and vegetables are allowed to sell by unit instead of weight, estimate average weight for unit"
"get customer data using the phone number provided in the user message prefix <client_phone>. with the tool get_customer_by_phone_number. using client_phone as argument"
"if do not know the customer name, Always ask for the customer's name at the beginning of the conversation,"
"The supermarket is located in Brazil and sells groceries and household items."
"Never ask for the customer phone number, it is provided in the user message<client_phone>."
"load products and use it to answer customer questions about products and prices."
"ask custommer name his name and use tool set_customer_contact to store it with the telephone number provided by in the begining of the user msg<client_phone>."
"if the customer ask for product list, load the product list use the tool load_products and provide options"
"The supermarket name is Bom preço Supermercados."
"It is located at 9 de Julho Avenue, 1234, São Paulo, SP, Brazil."
"Don't say the product list with prices befeore the customer ask for it."


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
        customer_manager.create_customer(
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


def set_customer_address(address: str, cellphone: str) -> str:
    """
    Store the customer's name for personalized interactions.
    Args:
        name (str): The customer's name
        cellphone (str): The customer's phone number
    Returns:
        str: Confirmation message
    """
    try:
        customer_manager.update_customer_address(cellphone, address)
        # logger.info(f"Stored customer name: {name} for cellphone: {cellphone}")
        return (
            f"Customer  adress{address} \n with phone: '{cellphone}' has been stored."
        )
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
        customer = customer_manager.get_customer(client_phone)
        logger.info(f"Retrieved customer: {client_phone} -> {customer}")
        return customer
    except Exception as e:
        logger.error(f"Error retrieving customer: {e}")
        return None


tools = [
    load_products,
    set_customer_contact,
    get_customer_by_phone_number,
    set_customer_address,
]


class AgentService:
    def __init__(self):
        checkpointer.setup()
        self.client = httpx.AsyncClient()
        self.gemini = GoogleLCService(checkpointer, prompt, tools)
        # self.deepseek = DeepSeekLCService(checkpointerprompt, tools)
        self.claude = ClaudeLCService(checkpointer, prompt, tools)
        self.chatgpt = None  # Placeholder for ChatGPT service if needed

    async def chat_completion(
        self,
        messages,
        session_id,
        client_phone,
        stream=False,
        prompt="",
    ) -> str | None:
        try:
            response = await self.claude.chat_completion(
                messages,
                session_id,
                client_phone,
                stream,
                prompt,
            )
            if response is not None:
                logger.info("CLAUDE response")
                logger.info(response)
                return response

            response = await self.gemini.chat_completion(
                messages,
                session_id,
                client_phone,
                stream,
                prompt,
            )
            if response is not None:
                logger.info("GEMINI response")
                logger.info(response)
                return response
            else:
                return None
        #            response = await self.deepseek.chat_completion(
        #                messages,
        #                session_id,
        #                client_phone,
        #                stream,
        #                prompt,
        #            )
        #            if response is not None:
        #                logger.info("DEEPSEEK response")
        #                logger.info(response)
        #                return response

        except Exception as e:
            logger.error(
                f"AgentService::chat_completion error for{client_phone}|session:{session_id} :with error => {str(e)}"
            )
            return None


# Initialize service with proper error handling
try:
    agent_service = AgentService()
except Exception as e:
    logger.error(f"Failed to initialize agent service: {e}")
    raise
