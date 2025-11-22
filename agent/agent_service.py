import logging
from typing import Any

import httpx
import pandas as pd
from langchain.tools import tool
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool

from agent.claude_langchain import ClaudeLCService
from agent.gemini_langchain import GoogleLCService
from config import settings
from sales.customer_management import CustomerManager
from sales.customer_schema import CustomerCreate

logger = logging.getLogger(__name__)

# Initialize database and services
connection_pool = ConnectionPool(
    conninfo=f"postgresql://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:5432/{settings.DB_NAME}?sslmode=disable",
    max_size=20,
    kwargs={"autocommit": True},
)
checkpointer = PostgresSaver(conn=connection_pool)
customer_manager = CustomerManager()

PROMPT = (
    "You are a helpful supermarket salesman. Be concise and accurate. "
    "Client phone is in <client_phone> tag. "
    "Get customer data using get_customer_by_phone_number tool. "
    "Ask for customer name if unknown. "
    "Bom preço Supermercados - 9 de Julho Avenue, 1234, São Paulo, SP, Brazil. "
    "Use load_products tool for product inquiries. "
    "Don't show prices before customer asks."
)


def _log(msg: str, level: str = "info") -> str:
    getattr(logger, level)(msg)
    return msg


@tool
def load_products() -> pd.DataFrame:
    """Load product list from produtos.xlsx."""
    try:
        return pd.read_excel("produtos.xlsx")
    except Exception as e:
        raise FileNotFoundError(f"Error loading products: {e}")


@tool
def set_customer_contact(name: str, cellphone: str) -> str:
    """Store customer name and phone."""
    try:
        customer_manager.create_customer(CustomerCreate(name=name, cellphone=cellphone))
        return _log(f"Customer '{name}' stored.")
    except Exception as e:
        return _log(f"Error storing customer: {e}", "error")


@tool
def set_customer_address(address: str, cellphone: str) -> str:
    """Store customer address."""
    try:
        customer_manager.update_customer_address(cellphone, address)
        return _log(f"Address stored for {cellphone}.")
    except Exception as e:
        return _log(f"Error storing address: {e}", "error")


@tool
def get_customer_by_phone_number(client_phone: str) -> Any | None:
    """Retrieve customer by phone number."""
    try:
        customer = customer_manager.get_customer(client_phone)
        logger.info(f"Retrieved customer: {client_phone}")
        return customer
    except Exception as e:
        logger.error(f"Error retrieving customer: {e}")
        return None


tools = [
    load_products,
    set_customer_contact,
    set_customer_address,
    get_customer_by_phone_number,
]


class AgentService:
    def __init__(self):
        checkpointer.setup()
        self.client = httpx.AsyncClient()
        self.services = [
            (ClaudeLCService(checkpointer, PROMPT, tools), "CLAUDE"),
            (GoogleLCService(checkpointer, PROMPT, tools), "GEMINI"),
        ]

    async def chat_completion(
        self, messages, session_id, client_phone, stream=False, prompt=""
    ) -> str | None:
        try:
            for service, name in self.services:
                response = await service.chat_completion(
                    messages, session_id, client_phone, stream, prompt
                )
                if response:
                    logger.info(f"{name} response: {response}")
                    return response
            return None
        except Exception as e:
            logger.error(f"chat_completion error for {client_phone}|{session_id}: {e}")
            return None


try:
    agent_service = AgentService()
except Exception as e:
    logger.error(f"Failed to initialize agent service: {e}")
    raise
