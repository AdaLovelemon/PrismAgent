import requests
import os
from typing import Optional, Literal
from src.search_utils import (
    parse_text_results, parse_image_results, parse_video_results,
    parse_place_results, parse_news_results, parse_shopping_results,
    parse_lens_results, parse_scholar_results
)

def text_search(
        user_query: str, 
        country: str = "cn", 
        language: str = "zh-cn", 
        page: int = 1,
        date_range: Literal["a", "h", "d", "w", "m", "y"] = "a",
        autocorrect: bool = True
    ) -> str:
    """
    Perform a Google text search.
    
    Args:
        user_query: The search query string.
        country: Two-letter country code (e.g., 'cn', 'us', 'gb').
        language: Language code (e.g., 'zh-cn', 'en').
        page: Result page number (default: 1).
        date_range: Limit results by time ('a': anytime, 'h': past hour, 'd': past day, 'w': past week, 'm': past month, 'y': past year).
        autocorrect: Whether to enable Google's search query autocorrect (default: True).
    
    Returns:
        A formatted string containing knowledge graph info and organic search results.
    """
    if date_range == 'a':
        query_prompt = {
            "q": user_query,
            "gl": country,
            "hl": language,
            "autocorrect": autocorrect,
            "page": page,
        }
    elif date_range in ['h', 'd', 'w', 'm', 'y']:
        query_prompt = {
        "q": user_query,
        "gl": country,
        "hl": language,
        "autocorrect": autocorrect,
        "tbs": f"qdr:{date_range}",
        "page": page,
        }
    else:
        raise ValueError("Invalid date_range value. Use 'a', 'h', 'd', 'w', 'm', or 'y'.")
    
    headers = {
        'X-API-KEY': os.getenv("SERPER_SEARCH_API_KEY"),
        'Content-Type': 'application/json'
    }

    response = requests.request(
        "POST", 
        url="https://google.serper.dev/search",
        headers=headers, 
        json=query_prompt
    )

    return parse_text_results(response.text)


def image_search(
        user_query: str, 
        country: str = "cn", 
        language: str = "zh-cn", 
        page: int = 1,
        image_num: int = 10,
        date_range: Literal["a", "h", "d", "w", "m", "y"] = "a",
        autocorrect: bool = True
    ) -> str:
    """
    Perform a Google image search.
    
    Args:
        user_query: The search query string for images.
        country: Two-letter country code.
        language: Language code.
        page: Result page number.
        image_num: Maximum number of images to return (default: 10).
        date_range: Limit results by time (default: 'a' for anytime).
        autocorrect: Whether to enable search query autocorrect.
    
    Returns:
        A formatted string containing titles, image URLs, and source links.
    """
    if date_range == 'a':
        query_prompt = {
            "q": user_query,
            "gl": country,
            "hl": language,
            "num": image_num,
            "autocorrect": autocorrect,
            "page": page,
        }
    elif date_range in ['h', 'd', 'w', 'm', 'y']:
        query_prompt = {
        "q": user_query,
        "gl": country,
        "hl": language,
        "num": image_num,
        "autocorrect": autocorrect,
        "tbs": f"qdr:{date_range}",
        "page": page,
        }
    else:
        raise ValueError("Invalid date_range value. Use 'a', 'h', 'd', 'w', 'm', or 'y'.")
    
    headers = {
        'X-API-KEY': os.getenv("SERPER_SEARCH_API_KEY"),
        'Content-Type': 'application/json'
    }

    response = requests.request(
        "POST", 
        url="https://google.serper.dev/images",
        headers=headers, 
        json=query_prompt
    )

    return parse_image_results(response.text)


def video_search(
        user_query: str, 
        country: str = "cn", 
        language: str = "zh-cn", 
        page: int = 1,
        date_range: Literal["a", "h", "d", "w", "m", "y"] = "a",
        autocorrect: bool = True
    ) -> str:
    """
    Perform a Google video search.
    
    Args:
        user_query: The search query string for videos.
        country: Two-letter country code.
        language: Language code.
        page: Result page number.
        date_range: Limit results by time.
        autocorrect: Whether to enable search query autocorrect.
    
    Returns:
        A formatted string containing video titles, links, channels, durations, and snippets.
    """
    if date_range == 'a':
        query_prompt = {
            "q": user_query,
            "gl": country,
            "hl": language,
            "autocorrect": autocorrect,
            "page": page,
        }
    elif date_range in ['h', 'd', 'w', 'm', 'y']:
        query_prompt = {
        "q": user_query,
        "gl": country,
        "hl": language,
        "autocorrect": autocorrect,
        "tbs": f"qdr:{date_range}",
        "page": page,
        }
    else:
        raise ValueError("Invalid date_range value. Use 'a', 'h', 'd', 'w', 'm', or 'y'.")
    
    headers = {
        'X-API-KEY': os.getenv("SERPER_SEARCH_API_KEY"),
        'Content-Type': 'application/json'
    }

    response = requests.request(
        "POST", 
        url="https://google.serper.dev/videos",
        headers=headers, 
        json=query_prompt
    )

    return parse_video_results(response.text)


def place_search(
        user_query: str,
        current_location: str,
        country: str = "cn", 
        language: str = "zh-cn", 
        page: int = 1,
        autocorrect: bool = True
    ) -> str:
    """
    Perform a Google maps/places search.
    
    Args:
        user_query: The query for people, places, or things (e.g., 'coffee', 'Apple Inc').
        current_location: The location to search around (e.g., 'Fort Lauderdale, FL').
        country: Two-letter country code.
        language: Language code.
        page: Result page number.
        autocorrect: Whether to enable search query autocorrect.
    
    Returns:
        A formatted string containing titles, addresses, ratings, and contact info for found places.
    """

    query_prompt = {
        "q": user_query,
        "location": current_location,
        "gl": country,
        "hl": language,
        "autocorrect": autocorrect,
        "page": page,
    }

    headers = {
        'X-API-KEY': os.getenv("SERPER_SEARCH_API_KEY"),
        'Content-Type': 'application/json'
    }

    response = requests.request(
        "POST", 
        url="https://google.serper.dev/places",
        headers=headers, 
        json=query_prompt
    )

    return parse_place_results(response.text)


def news_search(
        user_query: str, 
        country: str = "cn", 
        language: str = "zh-cn", 
        page: int = 1,
        date_range: Literal["a", "h", "d", "w", "m", "y"] = "d",
        autocorrect: bool = True
    ) -> str:
    """
    Perform a Google news search.
    
    Args:
        user_query: The search query string for news articles.
        country: Two-letter country code.
        language: Language code.
        page: Result page number.
        date_range: Limit results by time (default: 'd' for past day).
        autocorrect: Whether to enable search query autocorrect.
    
    Returns:
        A formatted string containing news titles, links, sources, publication dates, and snippets.
    """

    if date_range == 'a':
        query_prompt = {
            "q": user_query,
            "gl": country,
            "hl": language,
            "autocorrect": autocorrect,
            "page": page,
        }
    elif date_range in ['h', 'd', 'w', 'm', 'y']:
        query_prompt = {
        "q": user_query,
        "gl": country,
        "hl": language,
        "autocorrect": autocorrect,
        "tbs": f"qdr:{date_range}",
        "page": page,
        }
    else:
        raise ValueError("Invalid date_range value. Use 'a', 'h', 'd', 'w', 'm', or 'y'.")

    headers = {
        'X-API-KEY': os.getenv("SERPER_SEARCH_API_KEY"),
        'Content-Type': 'application/json'
    }

    response = requests.request(
        "POST", 
        url="https://google.serper.dev/news",
        headers=headers, 
        json=query_prompt
    )

    return parse_news_results(response.text)


def shopping_search(
        user_query: str, 
        country: str = "cn", 
        language: str = "zh-cn", 
        page: int = 1,
        autocorrect: bool = True
    ) -> str:
    """
    Perform a Google shopping search.
    
    Args:
        user_query: The search query string for products.
        country: Two-letter country code.
        language: Language code.
        page: Result page number.
        autocorrect: Whether to enable search query autocorrect.
    
    Returns:
        A formatted string containing product titles, prices, sources, and links.
    """

    
    query_prompt = {
        "q": user_query,
        "gl": country,
        "hl": language,
        "autocorrect": autocorrect,
        "page": page,
    }

    headers = {
        'X-API-KEY': os.getenv("SERPER_SEARCH_API_KEY"),
        'Content-Type': 'application/json'
    }

    response = requests.request(
        "POST", 
        url="https://google.serper.dev/shopping",
        headers=headers, 
        json=query_prompt
    )

    return parse_shopping_results(response.text)


def lens_search(
        image_url: str, 
        country: str = "cn", 
        language: str = "zh-cn", 
    ) -> str:
    """
    Perform a Google Lens visual search on an image URL.
    
    Args:
        image_url: The URL of the image to perform a visual search on.
        country: Two-letter country code.
        language: Language code.
    
    Returns:
        A formatted string containing visual search results (titles, links, and thumbnails).
    """

    
    query_prompt = {
        "url": image_url,
        "gl": country,
        "hl": language,
    }

    headers = {
        'X-API-KEY': os.getenv("SERPER_SEARCH_API_KEY"),
        'Content-Type': 'application/json'
    }

    response = requests.request(
        "POST", 
        url="https://google.serper.dev/lens",
        headers=headers, 
        json=query_prompt
    )

    return parse_lens_results(response.text)
        

def scholar_search(
        user_query: str, 
        country: str = "cn", 
        language: str = "zh-cn", 
        page: int = 1,
        autocorrect: bool = True
    ) -> str:
    """
    Perform a Google Scholar search for academic papers.
    
    Args:
        user_query: The search query string for papers/citations.
        country: Two-letter country code.
        language: Language code.
        page: Result page number.
        autocorrect: Whether to enable search query autocorrect.
    
    Returns:
        A formatted string containing paper titles, links, publication info, snippets, and citation counts.
    """

    
    query_prompt = {
        "q": user_query,
        "gl": country,
        "hl": language,
        "autocorrect": autocorrect,
        "page": page,
    }

    headers = {
        'X-API-KEY': os.getenv("SERPER_SEARCH_API_KEY"),
        'Content-Type': 'application/json'
    }

    response = requests.request(
        "POST", 
        url="https://google.serper.dev/scholar",
        headers=headers, 
        json=query_prompt
    )

    return parse_scholar_results(response.text)
