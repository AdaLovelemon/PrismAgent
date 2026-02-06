import json

def parse_text_results(json_data: str) -> str:
    """
    Parse the JSON response from a Serper text search into a formatted string.

    Args:
        json_data: The raw JSON string returned by the Serper API.

    Returns:
        A human-readable string containing Knowledge Graph info, organic results, 
        questions from "People Also Ask", and related searches.
    """
    data = json.loads(json_data)
    results = []
    
    if "knowledgeGraph" in data:
        kg = data["knowledgeGraph"]
        res = f"Knowledge Graph: {kg.get('title')} ({kg.get('type')})\n"
        res += f"Description: {kg.get('description')}\n"
        if "attributes" in kg:
            for k, v in kg["attributes"].items():
                res += f"{k}: {v}\n"
        results.append(res)
    
    if "organic" in data:
        results.append("Organic Results:")
        for item in data["organic"][:10]:
            # Use single line for each result to prevent newline-related extraction issues
            res = f"- Title: {item.get('title')} | Link: {item.get('link')} | Snippet: {item.get('snippet')}"
            results.append(res)
            
    if "peopleAlsoAsk" in data:
        results.append("People Also Ask:")
        for item in data["peopleAlsoAsk"]:
            results.append(f"- {item.get('question')} ({item.get('link')})")

    if "relatedSearches" in data:
        results.append("Related Searches:")
        for item in data["relatedSearches"]:
            results.append(f"- {item.get('query')} ({item.get('link')})")
            
    return "\n\n".join(results)

def parse_image_results(json_data: str) -> str:
    """
    Parse the JSON response from a Serper image search into a formatted string.

    Args:
        json_data: The raw JSON string returned by the Serper API.

    Returns:
        A formatted string listing the titles, image URLs, and source links of the top results.
    """
    data = json.loads(json_data)
    results = ["Image Results:"]
    if "images" in data:
        for item in data["images"][:10]:
            results.append(f"- Title: {item.get('title')} | Image URL: {item.get('imageUrl')} | Source Link: {item.get('link')}")
    return "\n\n".join(results)

def parse_video_results(json_data: str) -> str:
    """
    Parse the JSON response from a Serper video search into a formatted string.

    Args:
        json_data: The raw JSON string returned by the Serper API.

    Returns:
        A formatted string listing titles, links, sources, durations, dates, and snippets for top videos.
    """
    data = json.loads(json_data)
    results = ["Video Results:"]
    if "videos" in data:
        for item in data["videos"][:10]:
            res = f"- Title: {item.get('title')} | Link: {item.get('link')} | Source: {item.get('source')} ({item.get('channel')}) | Duration: {item.get('duration')} | Date: {item.get('date')} | Snippet: {item.get('snippet')}"
            results.append(res)
    return "\n\n".join(results)

def parse_place_results(json_data: str) -> str:
    """
    Parse the JSON response from a Serper places search into a formatted string.

    Args:
        json_data: The raw JSON string returned by the Serper API.

    Returns:
        A formatted string listing titles, addresses, ratings, and contact info for geographical places.
    """
    data = json.loads(json_data)
    results = ["Place Results:"]
    if "places" in data:
        for item in data["places"][:10]:
            res = f"- Title: {item.get('title')} | Address: {item.get('address')} | Category: {item.get('category')} | Rating: {item.get('rating')} ({item.get('ratingCount')} reviews) | Phone: {item.get('phoneNumber')} | Website: {item.get('website')}"
            results.append(res)
    return "\n\n".join(results)

def parse_news_results(json_data: str) -> str:
    """
    Parse the JSON response from a Serper news search into a formatted string.

    Args:
        json_data: The raw JSON string returned by the Serper API.

    Returns:
        A formatted string listing titles, links, sources, dates, and snippets of news articles.
    """
    data = json.loads(json_data)
    results = ["News Results:"]
    if "news" in data:
        for item in data["news"][:10]:
            res = f"- Title: {item.get('title')} | Link: {item.get('link')} | Source: {item.get('source')} ({item.get('date')}) | Snippet: {item.get('snippet')}"
            results.append(res)
    return "\n\n".join(results)

def parse_shopping_results(json_data: str) -> str:
    """
    Parse the JSON response from a Serper shopping search into a formatted string.

    Args:
        json_data: The raw JSON string returned by the Serper API.

    Returns:
        A formatted string listing product titles, prices, sources, links, and ratings.
    """
    data = json.loads(json_data)
    results = ["Shopping Results:"]
    if "shopping" in data:
        for item in data["shopping"][:10]:
            res = f"- Title: {item.get('title')} | Price: {item.get('price')} | Source: {item.get('source')} | Link: {item.get('link')} | Rating: {item.get('rating')} ({item.get('ratingCount')} reviews)"
            results.append(res)
    return "\n\n".join(results)

def parse_lens_results(json_data: str) -> str:
    """
    Parse the JSON response from a Serper Lens search into a formatted string.

    Args:
        json_data: The raw JSON string returned by the Serper API.

    Returns:
        A formatted string listing titles, links, and thumbnails for visually similar images.
    """
    data = json.loads(json_data)
    results = ["Lens Visual Search Results:"]
    if "organic" in data:
        for item in data["organic"][:10]:
            res = f"- Title: {item.get('title')} | Link: {item.get('link')} | Thumbnail: {item.get('thumbnailUrl')}"
            results.append(res)
    return "\n\n".join(results)

def parse_scholar_results(json_data: str) -> str:
    """
    Parse the JSON response from a Serper Scholar search into a formatted string.

    Args:
        json_data: The raw JSON string returned by the Serper API.

    Returns:
        A formatted string listing paper titles, links, publication info, snippets, 
        citation counts, and PDF links if available.
    """
    data = json.loads(json_data)
    results = ["Scholar Results:"]
    if "organic" in data:
        for item in data["organic"][:10]:
            res = f"- Title: {item.get('title')} | Link: {item.get('link')} | Publication: {item.get('publicationInfo')} | Snippet: {item.get('snippet')} | Cited by: {item.get('citedBy')}"
            if "pdfUrl" in item:
                res += f" | PDF Link: {item.get('pdfUrl')}"
            results.append(res)
    return "\n\n".join(results)

