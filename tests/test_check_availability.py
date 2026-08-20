"""Tests for the Day 4 check_availability MCP tool."""

import asyncio
from pathlib import Path
import sys
import unittest

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from library_mcp.database import get_book_availability, get_connection
from library_mcp.server import check_availability


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class DatabaseAvailabilityTests(unittest.TestCase):
    """Verify the focused read-only SQLite availability lookup."""

    def test_get_book_availability_for_existing_and_missing_books(self) -> None:
        available_book = get_book_availability(1)
        unavailable_book = get_book_availability(5)

        self.assertEqual(
            available_book,
            {
                "id": 1,
                "title": "Python Crash Course",
                "total_copies": 5,
                "available_copies": 3,
            },
        )
        self.assertEqual(unavailable_book["available_copies"], 0)
        self.assertIsNone(get_book_availability(9999))


class CheckAvailabilityTests(unittest.TestCase):
    """Verify validation, results, and stdio MCP behavior."""

    def test_reports_available_books(self) -> None:
        self.assertEqual(
            check_availability(1),
            {
                "success": True,
                "book_id": 1,
                "title": "Python Crash Course",
                "available": True,
                "available_copies": 3,
                "total_copies": 5,
            },
        )
        self.assertTrue(check_availability(4)["available"])

    def test_reports_unavailable_book_as_success(self) -> None:
        self.assertEqual(
            check_availability(5),
            {
                "success": True,
                "book_id": 5,
                "title": "Operating System Concepts",
                "available": False,
                "available_copies": 0,
                "total_copies": 5,
            },
        )

    def test_reports_missing_book(self) -> None:
        self.assertEqual(
            check_availability(9999),
            {"success": False, "book_id": 9999, "error": "Book not found"},
        )

    def test_rejects_non_positive_ids(self) -> None:
        for book_id in (0, -1, "1"):
            with self.subTest(book_id=book_id):
                with self.assertRaisesRegex(ValueError, "positive integer"):
                    check_availability(book_id)

    def test_calls_are_read_only(self) -> None:
        with get_connection() as connection:
            before_availability = [
                tuple(row)
                for row in connection.execute(
                    "SELECT id, available_copies FROM books ORDER BY id"
                ).fetchall()
            ]
            before_reservations = [
                tuple(row)
                for row in connection.execute(
                    "SELECT id, book_id, student_id, reserved_at, status "
                    "FROM reservations ORDER BY id"
                ).fetchall()
            ]

        check_availability(1)
        check_availability(1)
        check_availability(5)

        with get_connection() as connection:
            after_availability = [
                tuple(row)
                for row in connection.execute(
                    "SELECT id, available_copies FROM books ORDER BY id"
                ).fetchall()
            ]
            after_reservations = [
                tuple(row)
                for row in connection.execute(
                    "SELECT id, book_id, student_id, reserved_at, status "
                    "FROM reservations ORDER BY id"
                ).fetchall()
            ]

        self.assertEqual(before_availability[0], (1, 3))
        self.assertEqual(after_availability, before_availability)
        self.assertEqual(after_reservations, before_reservations)

    def test_stdio_client_discovers_schema_and_calls_tool(self) -> None:
        """Verify check_availability through the real stdio MCP path."""

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
                    availability_tool = next(
                        tool
                        for tool in tools.tools
                        if tool.name == "check_availability"
                    )
                    self.assertEqual(
                        availability_tool.input_schema["required"], ["book_id"]
                    )
                    self.assertEqual(
                        availability_tool.input_schema["properties"]["book_id"]["type"],
                        "integer",
                    )

                    available = await session.call_tool(
                        "check_availability", {"book_id": 1}
                    )
                    self.assertEqual(
                        available.structured_content["available_copies"], 3
                    )
                    self.assertTrue(available.structured_content["available"])

                    unavailable = await session.call_tool(
                        "check_availability", {"book_id": 5}
                    )
                    self.assertFalse(unavailable.structured_content["available"])
                    self.assertEqual(
                        unavailable.structured_content["available_copies"], 0
                    )

                    missing = await session.call_tool(
                        "check_availability", {"book_id": 9999}
                    )
                    self.assertEqual(
                        missing.structured_content["error"], "Book not found"
                    )

                    invalid = await session.call_tool(
                        "check_availability", {"book_id": 0}
                    )
                    self.assertTrue(invalid.is_error)
                    self.assertIn("positive integer", invalid.content[0].text)

        asyncio.run(verify_server())
