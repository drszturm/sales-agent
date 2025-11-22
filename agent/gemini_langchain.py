# pip3 install langchain_openai
# python3 deepseek_langchain.py
import getpass
import logging
import os

from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.postgres import PostgresSaver

from config import settings

# Uses the pickle module for serialization
# Make sure that you're only de-serializing trusted data
# (e.g., payloads that you have serialized yourself).
# Or implement a custom serializer.


if not os.getenv("GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY"] = getpass.getpass("Enter your GEMINI API key: ")
logger = logging.getLogger(__name__)


class GoogleLCService:
    def __init__(self, checkpointer: PostgresSaver, prompt: str, tools: list):
        self.api_key = settings.GEMINI_API_KEY

        self.model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=1.0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            # other params...
        )

        self.llm = create_agent(
            checkpointer=checkpointer,
            model=self.model,  # intalled model="claude-sonnet-4-5-20250929",
            tools=tools,
            system_prompt=prompt,
        )

    async def chat_completion(
        self,
        messages,
        session_id,
        client_phone,
        stream=False,
        prompt="",
    ):
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

            agent_response = (
                response["messages"][-1].content
                if isinstance(response["messages"][-1].content, str)
                else "\n".join(
                    [
                        str(response["text"])
                        for response in response["messages"][-1].content
                    ]
                )
            )

            return agent_response
        except Exception as e:
            logger.error(f"GoogleLCService chat_completion error: {str(e)}")
            return None
