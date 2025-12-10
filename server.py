from mcp.server.fastmcp import FastMCP
import time

import uuid

# Create an MCP server
mcp = FastMCP("DemoSkills")

@mcp.tool()
def calculate_sum(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

@mcp.tool()
def get_time() -> str:
    """Get the current time."""
    return time.ctime()

@mcp.tool()
def echo_reverse(text: str) -> str:
    """Reverse the given text."""
    return text[::-1]

@mcp.tool()
def generate_uuid() -> str:
    """Generate a random UUID."""
    return str(uuid.uuid4())

@mcp.tool()
def count_words(text: str) -> int:
    """Count the number of words in a string."""
    return len(text.split())

if __name__ == "__main__":
    mcp.run()
