"""
Web-based MCP Server for searching the web and fetching webpage content.

This server provides tools to perform various types of Google searches (text, images, videos, 
places, news, shopping, lens, scholar) via the Serper API and to fetch/parse content from URLs.
"""

from mcp.server.fastmcp import FastMCP
from src.serper_search import (
    text_search, image_search, video_search, place_search, 
    news_search, shopping_search, lens_search, scholar_search
)
from src.search_url import fetch_webpage_content

# Create an MCP server instance
mcp = FastMCP("Web-based Server")

# Register tools directly from their respective modules
mcp.tool(name="search_text")(text_search)
mcp.tool(name="search_image")(image_search)
mcp.tool(name="search_video")(video_search)
mcp.tool(name="search_place")(place_search)
mcp.tool(name="search_news")(news_search)
mcp.tool(name="search_shopping")(shopping_search)
mcp.tool(name="search_lens")(lens_search)
mcp.tool(name="search_scholar")(scholar_search)
mcp.tool(name="fetch_webpage")(fetch_webpage_content)

if __name__ == "__main__":
    # Run the server using stdio transport
    mcp.run(transport="stdio")


