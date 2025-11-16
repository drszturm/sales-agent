# python3 deepseek_langchain.py
import logging

import httpx
from psycopg_pool import ConnectionPool
from langgraph.checkpoint.postgres import PostgresSaver

from agent.deepseek_langchain_service import DeepSeekLCService
from agent.gemini_langchain import GoogleLCService

connection_pool = ConnectionPool(
    # Example configuration"postgresql://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:5432/{settings.DB_NAME}"
    conninfo="postgresql://postgres:ADMIN@localhost:5432/postgres?sslmode=disable",
    max_size=20,
)
checkpointer = PostgresSaver(conn=connection_pool)

# Uses the pickle module for serialization
# Make sure that you're only de-serializing trusted data
# (e.g., payloads that you have serialized yourself).
# Or implement a custom serializer.
# checkpointer = PostgresSaver(conn=pool)


logger = logging.getLogger(__name__)


class AgentService:
    def __init__(self):
        checkpointer.setup()
        self.client = httpx.AsyncClient()
        self.gemini = GoogleLCService(checkpointer)
        self.deepseek = DeepSeekLCService(checkpointer)
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
            response = await self.gemini.chat_completion(
                messages,
                session_id,
                client_phone,
                stream,
                prompt,
            )
            if response is not None:
                logger.info("GEMINI response")
                return response

            response = await self.deepseek.chat_completion(
                messages,
                session_id,
                client_phone,
                stream,
                prompt,
            )
            if response is not None:
                logger.info("DEEPSEEK response")
                return response
            else:
                logger.error(
                    f"AgentSerice::response failed for{client_phone}|session:{session_id}"
                )
                return None
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
