"""
Web-based MCP Server for searching the web and fetching webpage content.

This server provides tools to perform various types of Google searches (text, images, videos, 
places, news, shopping, lens, scholar) via the Serper API and to fetch/parse content from URLs.
"""

import argparse
import os
from mcp.server.fastmcp import FastMCP
from src.serper_search import (
    text_search, image_search, video_search, place_search, 
    news_search, shopping_search, lens_search, scholar_search
)
from src.search_url import fetch_webpage_content
from src.download_file import (
    download_file, 
    download_generic_file, 
    download_gdrive_file,
    download_video_audio,
    download_hf_file,
    download_github_content,
    set_sandbox_path
)

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
mcp.tool(name="download_generic_file")(download_generic_file)
mcp.tool(name="download_gdrive_file")(download_gdrive_file)
mcp.tool(name="download_video_audio")(download_video_audio)
mcp.tool(name="download_hf_file")(download_hf_file)
mcp.tool(name="download_github_content")(download_github_content)
mcp.tool(name="download_file")(download_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Web-based MCP Server")
    parser.add_argument("--sandbox-path", type=str, help="Path to the sandbox directory for downloads")
    args, unknown = parser.parse_known_args()

    if args.sandbox_path:
        set_sandbox_path(args.sandbox_path)

    # Run the server using stdio transport
    mcp.run(transport="stdio")


