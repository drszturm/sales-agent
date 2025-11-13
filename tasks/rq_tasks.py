"""RQ tasks that can be enqueued by the application.

These are thin, import-safe wrappers that call into the project's
sync/async code using asyncio.run so they can be executed by the RQ worker.
"""

from __future__ import annotations

import asyncio
from typing import Any

from agent.mcp_client import MCPClient
from messaging.evolution_client import evolution_client
from messaging.message_service import message_service
from models import MCPMessage, MCPRequest, SendMessageRequest


def send_message_task(
    number: str, text: str, options: dict[str, Any] | None = None
) -> Any:
    """Send a message via the Evolution API (callable by RQ).

    Args:
        number: recipient phone number
        text: message text
        options: optional payload options

    Returns:
        Response json from the Evolution API client
    """

    req = SendMessageRequest(number=number, text=text, options=options)

    # evolution_client.send_message is async; run it in an event loop
    return asyncio.run(evolution_client.send_message(req))


def process_webhook_task(payload: dict[str, Any]) -> bool:
    """Process an incoming webhook payload and forward to MCP, then reply.

    This mirrors the logic in `main.process_webhook_message` but is safe
    to import from within an RQ worker process.
    """

    # Extract message data (sync function)
    message_data = message_service.extract_message_data(payload.get("data", payload))

    if not message_data or not message_data.get("text"):
        return False

    phone_number = message_data.get("from")
    if not phone_number:
        return False

    session_id = f"whatsapp_{phone_number}"

    mcp_req = MCPRequest(
        messages=[MCPMessage(content=message_data["text"], role="user")],
        session_id=session_id,
        context={"platform": "whatsapp", "phone_number": phone_number},
    )

    mcp_client = MCPClient()
    mcp_response = asyncio.run(mcp_client.send_message(mcp_req))

    send_req = SendMessageRequest(number=phone_number, text=mcp_response.response)
    asyncio.run(evolution_client.send_message(send_req))

    return True


__all__ = ["send_message_task", "process_webhook_task"]
