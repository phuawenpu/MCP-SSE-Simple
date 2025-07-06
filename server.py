"""MCP SSE Server Example with FastAPI"""

from fastapi import FastAPI
from fastmcp import FastMCP

mcp: FastMCP = FastMCP("App")


@mcp.tool()
async def get_weather(city: str) -> str:
    """
    Get the weather information for a specified city.

    Args:
        city (str): The name of the city to get weather information for.

    Returns:
        str: A message containing the weather information for the specified city.
    """
    return f"The weather in {city} is sunny."


# Create FastAPI app and mount the SSE  MCP server
app = FastAPI()


@app.get("/test")
async def test():
    """
    Test endpoint to verify the server is running.

    Returns:
        dict: A simple hello world message.
    """
    return {"message": "Hello, world!"}


app.mount("/", mcp.sse_app())
