from agent.deepseek_langchain_service import deepseek_lc_service
from agent.deepseek_models import DeepSeekMessage
from agent.mcp_models import CallToolResult, ContentType, TextContent
from config import settings
from models import MCPRequest, MCPResponse


class MCPClient:
    def __init__(self) -> None:
        self.base_url = settings.MCP_SERVER_URL
        self.headers = {
            "Authorization": f"Bearer {settings.MCP_API_KEY}",
            "Content-Type": "application/json",
        }

    async def send_message(self, request: MCPRequest) -> MCPResponse:
        """Send message to MCP server and get response"""
        try:
            messages = []
            for msg in request.messages:
                messages.append(
                    DeepSeekMessage(
                        role="user",
                        content=f"<saleto${request.session_id}>\n\n" + msg.content,
                    )
                )

            ds_service = deepseek_lc_service
            result = await ds_service.chat_completion(
                messages=messages,
                session_id=request.session_id,
                client_phone=request.session_id,
            )

            CallToolResult(
                content=[TextContent(type=ContentType.TEXT, text=result.content)]
            )

            return MCPResponse(response=result.content)

        except Exception as e:
            # return MCPResponse(response=str(e))
            raise Exception(f"MCP Client HTTP error: {str(e)}") from e
