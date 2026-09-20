# import asyncio
# from fastmcp import FastMCP
# from mcp import ClientSession
# from mcp.client.sse import sse_client

# mcp = FastMCP("Shubham Server Proxy")

# REMOTE_MCP_URL = "https://xpense-tracker.fastmcp.app/mcp"

# # Register remote tools dynamically or proxy them:
# @mcp.tool()
# async def call_remote(endpoint: str = REMOTE_MCP_URL):
#     """Directly inspect or query the remote server."""
#     pass

# if __name__ == "__main__":
#     mcp.run()


import json
from fastmcp import FastMCP
from mcp import ClientSession
from mcp.client.sse import sse_client

mcp = FastMCP("Shubham Server Proxy")

REMOTE_MCP_URL = "https://expense-tracker-mcp-server-vd4k.onrender.com/sse"


async def forward_remote_tool(tool_name: str, arguments: dict):
    """Connects to the remote server via SSE and runs the requested tool."""
    async with sse_client(REMOTE_MCP_URL) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            # Return text or serialized content from remote response
            if hasattr(result, "content") and result.content:
                first_block = result.content[0]
                return getattr(first_block, "text", str(first_block))
            return result


# ============================================================
# INSPECTION / PASSTHROUGH TOOL
# ============================================================

@mcp.tool()
async def call_remote(tool_name: str, arguments_json: str = "{}"):
    """
    Directly query the remote server by tool name and JSON arguments.
    Example arguments_json: '{"start_date": "2026-01-01", "end_date": "2026-12-31"}'
    """
    try:
        args = json.loads(arguments_json)
    except Exception:
        args = {}
    return await forward_remote_tool(tool_name, args)


# ============================================================
# PROXIED EXPENSE TRACKER TOOLS
# ============================================================

@mcp.tool()
async def add_expense(
    date: str,
    amount: float,
    category: str,
    subcategory: str = "",
    note: str = ""
):
    """Add a new expense entry via remote server."""
    return await forward_remote_tool(
        "add_expense",
        {
            "date": date,
            "amount": amount,
            "category": category,
            "subcategory": subcategory,
            "note": note,
        },
    )
@mcp.tool()
async def edit_expense(
    expense_id: int,
    date: str = None,
    amount: float = None,
    category: str = None,
    subcategory: str = None,
    note: str = None
):
    """Edit an existing expense via remote server."""
    args = {"expense_id": expense_id}
    if date is not None:
        args["date"] = date
    if amount is not None:
        args["amount"] = amount
    if category is not None:
        args["category"] = category
    if subcategory is not None:
        args["subcategory"] = subcategory
    if note is not None:
        args["note"] = note
    return await forward_remote_tool("edit_expense", args)


@mcp.tool()
async def delete_expense(expense_id: int):
    """Delete an expense by ID via remote server."""
    return await forward_remote_tool("delete_expense", {"expense_id": expense_id})


@mcp.tool()
async def list_expenses(start_date: str, end_date: str):
    """List expense entries within an inclusive date range via remote server."""
    return await forward_remote_tool(
        "list_expenses",
        {"start_date": start_date, "end_date": end_date},
    )


@mcp.tool()
async def summarize(start_date: str, end_date: str, category: str = None):
    """Summarize expenses by category via remote server."""
    args = {"start_date": start_date, "end_date": end_date}
    if category is not None:
        args["category"] = category
    return await forward_remote_tool("summarize", args)


@mcp.tool()
async def add_credit(date: str, amount: float, source: str = "", note: str = ""):
    """Add credit to the account via remote server."""
    return await forward_remote_tool(
        "add_credit",
        {"date": date, "amount": amount, "source": source, "note": note},
    )


@mcp.tool()
async def list_credits(start_date: str, end_date: str):
    """List credits within an inclusive date range via remote server."""
    return await forward_remote_tool(
        "list_credits",
        {"start_date": start_date, "end_date": end_date},
    )


@mcp.tool()
async def delete_credit(credit_id: int):
    """Delete a credit entry by ID via remote server."""
    return await forward_remote_tool("delete_credit", {"credit_id": credit_id})


@mcp.tool()
async def account_summary(start_date: str, end_date: str):
    """Show total credits, total expenses, and net balance via remote server."""
    return await forward_remote_tool(
        "account_summary",
        {"start_date": start_date, "end_date": end_date},
    )


if __name__ == "__main__":
    mcp.run()