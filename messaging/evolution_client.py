import logging
from typing import Any

import httpx

from config import settings
from models import SendMediaRequest, SendMessageRequest
from shared.metrics import instrument

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EvolutionClient:
    def __init__(self) -> None:
        self.base_url = settings.EVOLUTION_API_BASE_URL
        self.headers = {
            "apikey": settings.EVOLUTION_API_KEY,
            "Content-Type": "application/json",
        }
        self.client = httpx.AsyncClient()

    @instrument
    async def send_message(self, request: SendMessageRequest) -> None:
        """Send text message via Evolution API"""
        try:
            payload = {
                "number": request.number,
                "text": request.text,
                **({"options": request.options} if request.options else {}),
            }
            logger.debug(f"Evolution API request payload: {payload}")
            await self.client.post(
                f"{self.base_url}/message/sendtext/mcp",
                json=payload,
                headers=self.headers,
            )

            return
        except Exception as e:
            logger.error(f"Evolution API HTTP error: {str(e)}")
            raise Exception(f"Evolution API HTTP error: {str(e)}") from e

    @instrument
    async def send_media(self, request: SendMediaRequest) -> Any:
        """Send media message via Evolution API"""
        async with httpx.AsyncClient() as client:
            payload = {
                "number": request.number,
                "media": request.media,
                "fileName": request.fileName,
                "caption": request.caption,
                **({"options": request.options} if request.options else {}),
            }

            response = await client.post(
                f"{self.base_url}/message/sendMedia/{request.number}",
                json=payload,
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()

    @instrument
    async def get_instance_info(self, instance: str) -> Any:
        """Get information about a specific instance"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/instance/info/{instance}", headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    @instrument
    async def set_webhook(self, instance: str) -> Any:
        """Set webhook for receiving messages"""
        async with httpx.AsyncClient() as client:
            payload = {
                "webhook": settings.WEBHOOK_URL,
                "enabled": True,
                "webhook_by_events": False,
            }

            response = await client.post(
                f"{self.base_url}/instance/setWebhook/{instance}",
                json=payload,
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()


evolution_client = EvolutionClient()
