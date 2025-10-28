from typing import Any

import mcp.types as types
from pydantic import BaseModel, model_validator


class ServerConfig(BaseModel):
    command: str | None = None
    args: list[str] = []
    env: dict[str, str] = {}
    url: str | None = None
    headers: dict[str, Any] = {}

    @model_validator(mode="after")
    def check_command_or_url(self):
        if not self.command and not self.url:
            raise ValueError("Either 'command' or 'url' must be provided")
        return self


class Server(BaseModel):
    """Definition for a server the client can connect."""

    name: str
    """The name of the server."""
    description: str | None = None
    """A human-readable description of the server."""
    config: ServerConfig
    """The configuration for the server."""

    tools: list[types.Tool] | None = None
    """The tools available on the server."""

# 建议注释/说明：
# ServerConfig: 描述如何连接 server （command/args/env OR url/headers）
# Server: 表示一个远端 MCP server 的元数据和工具列表。
# 
# 动态工具支持建议（非强制修改模型）：
# - 推荐在未来为 Server 增加两个可选字段（示例，仅注释，不改动模型）：
#     exposed_tools: list[str] | None = None  # 仅在 registry 中被暴露的工具名（优先级高）
#     all_tools: list[types.Tool] | None = None  # 原始从 server 列出的完整工具清单
# - 运行时：MCPConnection.list_tools() 填充 server.tools（all_tools），但在返回给 agent 时，Router/registry 会决定 exposed_tools。
# 
# 以上方案可以让你在不改动 types.Tool 的情况下实现“只给 agent 部分工具”的行为。
