"""

class ToolRegistry:
    # ToolRegistry 管理每个 server 上当前“暴露”给 agent 的工具集合。
    # 设计要点：
    # - 内存中维护 { server_name: set(tool_name, ...) } 结构
    # - 提供线程/协程安全的方法用于增删/查询（示例使用 asyncio.Lock）
    # - 支持从 Router 的 server 全量工具列表初始化 registry（默认可先暴露全部或部分）
    # - expose_tool/hide_tool/list_exposed/is_exposed 为常用接口

    def __init__(self):
        import asyncio
        self._registry: dict[str, set[str]] = {}
        self._lock = asyncio.Lock()

    async def initialize_from_servers(self, servers: dict):
        # servers: dict of Server models keyed by name (Router.servers)
        # 默认策略：可选择只暴露部分工具（例如前 N 个），或全部暴露。
        # 示例中默认全部暴露，可在此处实现策略（注释中提示如何改为部分暴露）。
        async with self._lock:
            for name, server in servers.items():
                # server.tools 可能是 None/[] 或 list[types.Tool]
                tools = getattr(server, "tools", None) or []
                # 示例策略：只暴露前 K 个工具。将 K 改为你想要的子集大小。
                K = 3  # 可配置
                tool_names = [t.name for t in tools[:K]]
                self._registry[name] = set(tool_names)

    async def expose_tool(self, server_name: str, tool_name: str):
        async with self._lock:
            self._registry.setdefault(server_name, set()).add(tool_name)

    async def hide_tool(self, server_name: str, tool_name: str):
        async with self._lock:
            if server_name in self._registry:
                self._registry[server_name].discard(tool_name)

    async def list_exposed(self, server_name: str) -> list[str]:
        async with self._lock:
            return list(self._registry.get(server_name, set()))

    async def is_exposed(self, server_name: str, tool_name: str) -> bool:
        async with self._lock:
            return tool_name in self._registry.get(server_name, set())
"""