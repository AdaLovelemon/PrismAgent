# Web-based MCP Server

This MCP (Model Context Protocol) server provides tools for web searching and webpage content fetching. It leverages the [Serper API](https://serper.dev/) for various Google search types and uses `BeautifulSoup` for parsing webpage content.

## Features

- **Text Search**: Standard Google search results including organic links and knowledge graph information.
- **Image Search**: Finds images based on a query.
- **Video Search**: Searches for videos including duration and channel info.
- **News Search**: Latest news articles.
- **Shopping Search**: Product and price information.
- **Place Search**: Location-based search for businesses and points of interest.
- **Scholar Search**: Academic paper search via Google Scholar.
- **Lens Search**: Visual search from an image URL.
- **Webpage Fetching**: Retrieves cleaned text content and a list of images from any public URL.

## Configuration

### Environment Variables

You need to set the following environment variable for the search tools to work:

- `SERPER_SEARCH_API_KEY`: Your API key from [Serper](https://serper.dev/).

### Installation

```bash
pip install -r requirements.txt
# Or if using the pyproject.toml
pip install .
```

## Tools

### Search Tools
- `search_text(user_query, country, language, page, date_range, autocorrect)`
- `search_image(user_query, country, language, page, image_num, date_range, autocorrect)`
- `search_video(user_query, country, language, page, date_range, autocorrect)`
- `search_place(user_query, current_location, country, language, page, autocorrect)`
- `search_news(user_query, country, language, page, date_range, autocorrect)`
- `search_shopping(user_query, country, language, page, autocorrect)`
- `search_lens(image_url, country, language)`
- `search_scholar(user_query, country, language, page, autocorrect)`

### Utilities
- `fetch_webpage(url, timeout)`: Fetches cleaned text and image links from the specified URL.

## Usage

To run the server:

```bash
python server.py
```

The server uses `stdio` transport by default.

## License

MIT
