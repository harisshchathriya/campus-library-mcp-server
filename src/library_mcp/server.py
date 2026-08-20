"""MCP server entry point for the Campus Library project."""

from mcp.server.mcpserver import MCPServer

from library_mcp.database import get_book_availability, search_books


app = MCPServer(
    name="Campus Library MCP Server",
    title="Campus Library MCP Server",
)


@app.tool(description="Confirm that the Campus Library MCP server is available.")
def health_check() -> dict[str, str]:
    """Return a small response used to verify MCP tool registration."""
    return {
        "status": "ok",
        "service": "Campus Library MCP Server",
    }


@app.tool(
    description=(
        "Search the library catalog by a required text query. Searches book titles, "
        "authors, and categories and returns matching catalog details."
    )
)
def search_book(query: str) -> dict[str, object]:
    """Search the catalog using a normalized, non-empty query."""
    normalized_query = query.strip()
    if not normalized_query:
        raise ValueError("query must not be empty or whitespace-only")

    books = search_books(normalized_query)
    return {
        "success": True,
        "query": normalized_query,
        "count": len(books),
        "books": books,
    }


@app.tool(
    description=(
        "Check the current availability of one specific library book using its "
        "book_id. This reports copy counts only; it does not reserve or modify "
        "the book."
    )
)
def check_availability(book_id: int) -> dict[str, bool | int | str]:
    """Return current copy availability for a valid positive book ID."""
    if isinstance(book_id, bool) or not isinstance(book_id, int) or book_id <= 0:
        raise ValueError("book_id must be a positive integer")

    book = get_book_availability(book_id)
    if book is None:
        return {
            "success": False,
            "book_id": book_id,
            "error": "Book not found",
        }

    available_copies = book["available_copies"]
    total_copies = book["total_copies"]
    title = book["title"]
    stored_book_id = book["id"]
    assert isinstance(available_copies, int)
    assert isinstance(total_copies, int)
    assert isinstance(title, str)
    assert isinstance(stored_book_id, int)

    return {
        "success": True,
        "book_id": stored_book_id,
        "title": title,
        "available": available_copies > 0,
        "available_copies": available_copies,
        "total_copies": total_copies,
    }


def main() -> None:
    """Run the server over the MCP stdio transport."""
    app.run(transport="stdio")


if __name__ == "__main__":
    main()
