"""Focused checks for the Day 2 MCP server foundation."""

import asyncio
from pathlib import Path
import sys
import unittest

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from library_mcp.server import app, health_check


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ServerTests(unittest.TestCase):
    """Verify server initialization and the temporary health-check tool."""

    def test_server_has_expected_name(self) -> None:
        self.assertEqual(app.name, "Campus Library MCP Server")

    def test_health_check_returns_expected_response(self) -> None:
        self.assertEqual(
            health_check(),
            {"status": "ok", "service": "Campus Library MCP Server"},
        )

    def test_health_check_is_registered(self) -> None:
        tools = asyncio.run(app.list_tools())
        self.assertEqual(
            [tool.name for tool in tools], ["health_check", "search_book"]
        )

    def test_stdio_client_discovers_and_calls_health_check(self) -> None:
        """Verify initialization, discovery, and invocation over stdio."""

        async def verify_server() -> None:
            parameters = StdioServerParameters(
                command=sys.executable,
                args=["-m", "library_mcp.server"],
                env={"PYTHONPATH": str(PROJECT_ROOT / "src")},
                cwd=PROJECT_ROOT,
            )
            async with stdio_client(parameters) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    initialized = await session.initialize()
                    tools = await session.list_tools()
                    result = await session.call_tool("health_check")

                    self.assertEqual(initialized.server_info.name, "Campus Library MCP Server")
                    self.assertEqual(
                        [tool.name for tool in tools.tools],
                        ["health_check", "search_book"],
                    )
                    self.assertEqual(
                        result.structured_content,
                        {"status": "ok", "service": "Campus Library MCP Server"},
                    )

        asyncio.run(verify_server())


if __name__ == "__main__":
    unittest.main()
