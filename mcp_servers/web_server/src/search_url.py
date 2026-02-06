import requests
import time
import random
from bs4 import BeautifulSoup
from typing import Optional, List
from urllib.parse import urljoin, urlparse

# Global state to track access timing per domain
_LAST_ACCESS_TIMES = {}

def _wait_for_politeness(url: str):
    """
    Implements a domain-aware delay to prevent IP blocking.
    - Same domain: Wait 3-6 seconds since last access.
    - Different domain: Mini jitter (0.5-1.5s) to look more human-like.
    """
    domain = urlparse(url).netloc
    if not domain:
        return
        
    now = time.time()
    last_time = _LAST_ACCESS_TIMES.get(domain, 0)
    elapsed = now - last_time
    
    if elapsed < 3.0:
        # Calculate how much more we need to wait
        wait_time = random.uniform(3.0, 6.0) - elapsed
        if wait_time > 0:
            time.sleep(wait_time)
    else:
        # Basic jitter for even first-time domains
        time.sleep(random.uniform(0.5, 1.5))
        
    _LAST_ACCESS_TIMES[domain] = time.time()

def fetch_webpage_content(url: str, timeout: int = 15) -> str:
    """
    Fetch the text and image content of a specific webpage URL with safety delays.
    
    Args:
        url: The URL of the webpage to access.
        timeout: Request timeout in seconds.
        
    Returns:
        The cleaned text content and a list of images, or an error message.
    """
    _wait_for_politeness(url)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
    }
    
    # Using a session for better connection management
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        # Initial request to the target URL
        response = session.get(url, timeout=timeout)
        
        # Simple retry mechanism for 429 Too Many Requests
        if response.status_code == 429:
            time.sleep(random.uniform(5, 10))
            response = session.get(url, timeout=timeout)
            
        response.raise_for_status()
        
        # Determine encoding to handle different character sets correctly
        if response.encoding == 'ISO-8859-1':
            response.encoding = response.apparent_encoding
            
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. Extract Images: Get source URL and alt text
        images = []
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                abs_src = urljoin(url, src)
                alt = img.get('alt', '').strip()
                # Use a single line for image info to avoid issues with newlines in storage/parsing
                images.append(f"- Image: {abs_src} | Alt: {alt}" if alt else f"- Image: {abs_src}")
        
        # 2. Remove noise elements: Strip out non-content HTML tags
        for script_or_style in soup(["script", "style", "header", "footer", "nav", "aside", "form"]):
            script_or_style.decompose()

        # 3. Get text content: Extract visible text and clean whitespace
        text = soup.get_text(separator='\n')
        
        # Basic cleaning of multiple spaces and empty lines
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        cleaned_text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # 4. Construct final output: Include URL, text content, and images
        result = [f"URL: {url}", "\n--- PAGE TEXT CONTENT ---", cleaned_text[:12000]] # Slightly increased limit
        
        if images:
            result.append("\n--- IMAGES FOUND ON PAGE ---")
            result.extend(images[:20]) 
            
        return "\n".join(result)

        
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code
        if status == 403:
            return f"Error: HTTP 403 Forbidden. This site might be blocking automated access (e.g. Cloudflare protected)."
        return f"Error: HTTP {status} when accessing {url}"
    except Exception as e:
        return f"Error: Unable to fetch page content: {str(e)}"
