"""Tests for the Day 3 search_book MCP tool."""

import asyncio
from pathlib import Path
import sys
import unittest

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from library_mcp.database import search_books
from library_mcp.server import health_check, search_book


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class DatabaseSearchTests(unittest.TestCase):
    """Verify the focused SQLite search operation."""

    def test_searches_title_author_category_and_no_results(self) -> None:
        self.assertEqual(
            [book["title"] for book in search_books("Python")],
            [
                "Python Crash Course",
                "Data Structures and Algorithms in Python",
            ],
        )
        self.assertEqual(
            [book["title"] for book in search_books("Silberschatz")],
            ["Database System Concepts", "Operating System Concepts"],
        )
        self.assertEqual(
            [book["title"] for book in search_books("Programming")],
            ["Python Crash Course", "Clean Code"],
        )
        self.assertEqual(search_books("XYZ123"), [])


class SearchBookTests(unittest.TestCase):
    """Verify validation and structured search results."""

    def test_case_insensitive_search(self) -> None:
        self.assertEqual(
            search_book("python")["books"], search_book("PYTHON")["books"]
        )

    def test_whitespace_is_normalized(self) -> None:
        self.assertEqual(
            search_book("  Python  "),
            search_book("Python"),
        )

    def test_no_results_are_successful(self) -> None:
        self.assertEqual(
            search_book("XYZ123"),
            {"success": True, "query": "XYZ123", "count": 0, "books": []},
        )

    def test_empty_queries_are_rejected(self) -> None:
        for query in ("", "   "):
            with self.subTest(query=query):
                with self.assertRaisesRegex(ValueError, "query must not be empty"):
                    search_book(query)

    def test_stdio_client_discovers_and_calls_search_book(self) -> None:
        """Verify search_book through the real stdio MCP path."""

        async def verify_server() -> None:
            parameters = StdioServerParameters(
                command=sys.executable,
                args=["-m", "library_mcp.server"],
                env={"PYTHONPATH": str(PROJECT_ROOT / "src")},
                cwd=PROJECT_ROOT,
            )
            async with stdio_client(parameters) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    tools = await session.list_tools()
                    search_tool = next(
                        tool for tool in tools.tools if tool.name == "search_book"
                    )
                    self.assertEqual(
                        search_tool.input_schema["required"], ["query"]
                    )

                    python_result = await session.call_tool(
                        "search_book", {"query": "Python"}
                    )
                    self.assertTrue(python_result.structured_content["success"])
                    self.assertEqual(python_result.structured_content["count"], 2)

                    no_results = await session.call_tool(
                        "search_book", {"query": "XYZ123"}
                    )
                    self.assertEqual(
                        no_results.structured_content,
                        {"success": True, "query": "XYZ123", "count": 0, "books": []},
                    )

                    invalid_result = await session.call_tool(
                        "search_book", {"query": "   "}
                    )
                    self.assertTrue(invalid_result.is_error)
                    self.assertIn("query must not be empty", invalid_result.content[0].text)

        asyncio.run(verify_server())

    def test_health_check_regression(self) -> None:
        self.assertEqual(
            health_check(),
            {"status": "ok", "service": "Campus Library MCP Server"},
        )
