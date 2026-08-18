"""MCP server entry point for the Campus Library project."""

from mcp.server.mcpserver import MCPServer


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


def main() -> None:
    """Run the server over the MCP stdio transport."""
    app.run(transport="stdio")


if __name__ == "__main__":
    main()
