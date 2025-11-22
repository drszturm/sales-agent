# pip3 install langchain_openai
# python3 deepseek_langchain.py
import getpass
import logging
import os

from langchain.agents import create_agent
from langchain_deepseek import ChatDeepSeek
from langgraph.checkpoint.postgres import PostgresSaver

from config import settings

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
# tools call for deekseek langchain service not working well


class DeepSeekLCService:
    def __init__(self, checkpointer: PostgresSaver, prompt: str, tools: list):
        self.api_key = settings.DEEPSEEK_API_KEY

        self.llm = create_agent(
            checkpointer=checkpointer,
            model=model,  # intalled model="claude-sonnet-4-5-20250929",
            tools=[],
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

            return response["messages"][-1].content
        except Exception as e:
            logger.error(f"DeepSeekLCService chat_completion error: {str(e)}")
            return None
            raise
