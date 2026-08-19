"""MCP server entry point for the Campus Library project."""

from mcp.server.mcpserver import MCPServer

from library_mcp.database import search_books


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


def main() -> None:
    """Run the server over the MCP stdio transport."""
    app.run(transport="stdio")


if __name__ == "__main__":
    main()
